#!/bin/bash
# Enhanced PostgreSQL Startup Script for Mini LLM Chat
# This script provides comprehensive PostgreSQL setup and startup with error handling

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_NAME="Mini LLM Chat PostgreSQL Launcher"
VERSION="1.0.0"
DEFAULT_DB_NAME="mini_llm_chat"
DEFAULT_DB_URL="postgresql:///$DEFAULT_DB_NAME"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

# Function to show usage
show_usage() {
    cat << EOF
$SCRIPT_NAME v$VERSION

USAGE:
    $0 [OPTIONS] [-- ADDITIONAL_CLI_ARGS]

OPTIONS:
    -h, --help              Show this help message
    -v, --version           Show version information
    -d, --database NAME     Database name (default: $DEFAULT_DB_NAME)
    -u, --url URL           Custom database URL
    -s, --setup             Run database setup (init-db and setup-admin)
    -i, --init-only         Initialize database tables only
    -a, --admin-only        Setup admin user only
    -f, --fallback          Enable fallback to memory mode
    -q, --quiet             Suppress non-error output
    --debug                 Enable debug logging
    --dry-run               Show what would be executed without running

EXAMPLES:
    $0                      # Start with default PostgreSQL settings
    $0 --setup              # Initialize database and setup admin user
    $0 -d myapp             # Use custom database name
    $0 -u postgresql://user:pass@host:5432/db  # Use custom URL
    $0 --fallback           # Enable automatic fallback to memory mode
    $0 -- --max-calls 10    # Pass additional arguments to CLI

ENVIRONMENT VARIABLES:
    DATABASE_URL            PostgreSQL connection URL
    OPENAI_API_KEY         Your OpenAI API key (required)
    DB_BACKEND             Database backend preference
    LOG_LEVEL              Logging level (DEBUG, INFO, WARNING, ERROR)

For more information, see POSTGRESQL_INITIALIZATION_GUIDE.md
EOF
}

# Function to show version
show_version() {
    echo "$SCRIPT_NAME v$VERSION"
    echo "Mini LLM Chat PostgreSQL startup script"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check PostgreSQL installation
check_postgresql_installation() {
    print_info "Checking PostgreSQL installation..."
    
    if ! command_exists psql; then
        print_error "PostgreSQL client (psql) not found"
        print_error "Please install PostgreSQL and try again"
        echo
        echo "Installation commands:"
        echo "  Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
        echo "  CentOS/RHEL:   sudo yum install postgresql-server postgresql-contrib"
        echo "  macOS:         brew install postgresql"
        echo "  Windows:       Download from https://www.postgresql.org/download/"
        return 1
    fi
    
    if command_exists pg_config; then
        local pg_version=$(pg_config --version 2>/dev/null || echo "Unknown")
        print_success "PostgreSQL found: $pg_version"
    else
        print_success "PostgreSQL client found"
    fi
    
    return 0
}

# Function to check if PostgreSQL service is running
check_postgresql_service() {
    print_info "Checking PostgreSQL service status..."
    
    # Try pg_isready first (most reliable)
    if command_exists pg_isready; then
        if pg_isready -q 2>/dev/null; then
            print_success "PostgreSQL service is running"
            return 0
        fi
    fi
    
    # Platform-specific checks
    case "$(uname -s)" in
        Linux*)
            if command_exists systemctl; then
                if systemctl is-active --quiet postgresql 2>/dev/null; then
                    print_success "PostgreSQL service is running"
                    return 0
                fi
            elif command_exists service; then
                if service postgresql status >/dev/null 2>&1; then
                    print_success "PostgreSQL service is running"
                    return 0
                fi
            fi
            ;;
        Darwin*)
            if command_exists brew; then
                if brew services list | grep -q "postgresql.*started" 2>/dev/null; then
                    print_success "PostgreSQL service is running"
                    return 0
                fi
            fi
            ;;
    esac
    
    print_warning "PostgreSQL service is not running"
    return 1
}

# Function to start PostgreSQL service
start_postgresql_service() {
    print_info "Attempting to start PostgreSQL service..."
    
    case "$(uname -s)" in
        Linux*)
            if command_exists systemctl; then
                print_info "Starting PostgreSQL with systemctl..."
                if sudo systemctl start postgresql 2>/dev/null; then
                    print_success "PostgreSQL service started"
                    return 0
                fi
            elif command_exists service; then
                print_info "Starting PostgreSQL with service command..."
                if sudo service postgresql start 2>/dev/null; then
                    print_success "PostgreSQL service started"
                    return 0
                fi
            fi
            ;;
        Darwin*)
            if command_exists brew; then
                print_info "Starting PostgreSQL with brew..."
                if brew services start postgresql 2>/dev/null; then
                    print_success "PostgreSQL service started"
                    return 0
                fi
            fi
            ;;
    esac
    
    print_error "Failed to start PostgreSQL service"
    print_error "Please start PostgreSQL manually and try again"
    return 1
}

# Function to check database existence
check_database_exists() {
    local db_name="$1"
    print_info "Checking if database '$db_name' exists..."
    
    if psql -lqt | cut -d \| -f 1 | grep -qw "$db_name" 2>/dev/null; then
        print_success "Database '$db_name' exists"
        return 0
    else
        print_warning "Database '$db_name' does not exist"
        return 1
    fi
}

# Function to create database
create_database() {
    local db_name="$1"
    print_info "Creating database '$db_name'..."
    
    if createdb "$db_name" 2>/dev/null; then
        print_success "Database '$db_name' created successfully"
        return 0
    else
        print_error "Failed to create database '$db_name'"
        print_error "Please create the database manually: createdb $db_name"
        return 1
    fi
}

# Function to test database connection
test_database_connection() {
    local db_url="$1"
    print_info "Testing database connection..."
    
    # Extract database name from URL for connection test
    local db_name
    if [[ "$db_url" =~ postgresql://.*/(.*) ]]; then
        db_name="${BASH_REMATCH[1]}"
    elif [[ "$db_url" =~ postgresql:///(.+) ]]; then
        db_name="${BASH_REMATCH[1]}"
    else
        db_name="$DEFAULT_DB_NAME"
    fi
    
    if psql -d "$db_name" -c "SELECT 1;" >/dev/null 2>&1; then
        print_success "Database connection successful"
        return 0
    else
        print_error "Database connection failed"
        return 1
    fi
}

# Function to setup PostgreSQL environment
setup_postgresql() {
    local db_name="$1"
    local db_url="$2"
    
    print_header "PostgreSQL Environment Setup"
    
    # Check installation
    if ! check_postgresql_installation; then
        return 1
    fi
    
    # Check and start service if needed
    if ! check_postgresql_service; then
        if ! start_postgresql_service; then
            return 1
        fi
        # Wait a moment for service to fully start
        sleep 2
    fi
    
    # Check and create database if needed
    if ! check_database_exists "$db_name"; then
        if ! create_database "$db_name"; then
            return 1
        fi
    fi
    
    # Test connection
    if ! test_database_connection "$db_url"; then
        return 1
    fi
    
    print_success "PostgreSQL environment is ready"
    return 0
}

# Function to run database initialization
run_database_init() {
    local db_url="$1"
    local fallback_flag="$2"
    
    print_header "Database Initialization"
    
    local cmd="python -m mini_llm_chat.cli --init-db --db-backend postgresql"
    
    if [[ -n "$db_url" ]]; then
        cmd="$cmd --database-url '$db_url'"
    fi
    
    if [[ "$fallback_flag" == "true" ]]; then
        cmd="$cmd --fallback-to-memory"
    fi
    
    print_info "Running: $cmd"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_info "[DRY RUN] Would execute: $cmd"
        return 0
    fi
    
    if eval "$cmd"; then
        print_success "Database initialization completed"
        return 0
    else
        print_error "Database initialization failed"
        return 1
    fi
}

# Function to run admin setup
run_admin_setup() {
    local db_url="$1"
    local fallback_flag="$2"
    
    print_header "Admin User Setup"
    
    local cmd="python -m mini_llm_chat.cli --setup-admin --db-backend postgresql"
    
    if [[ -n "$db_url" ]]; then
        cmd="$cmd --database-url '$db_url'"
    fi
    
    if [[ "$fallback_flag" == "true" ]]; then
        cmd="$cmd --fallback-to-memory"
    fi
    
    print_info "Running: $cmd"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_info "[DRY RUN] Would execute: $cmd"
        return 0
    fi
    
    if eval "$cmd"; then
        print_success "Admin user setup completed"
        return 0
    else
        print_error "Admin user setup failed"
        return 1
    fi
}

# Function to start the application
start_application() {
    local db_url="$1"
    local fallback_flag="$2"
    local additional_args="$3"
    local log_level="$4"
    
    print_header "Starting Mini LLM Chat"
    
    # Set environment variables
    export DATABASE_URL="$db_url"
    
    # Build command
    local cmd="python -m mini_llm_chat.cli --db-backend postgresql"
    
    if [[ -n "$db_url" ]]; then
        cmd="$cmd --database-url '$db_url'"
    fi
    
    if [[ "$fallback_flag" == "true" ]]; then
        cmd="$cmd --fallback-to-memory"
    fi
    
    if [[ -n "$log_level" ]]; then
        cmd="$cmd --log-level $log_level"
    fi
    
    if [[ -n "$additional_args" ]]; then
        cmd="$cmd $additional_args"
    fi
    
    print_info "Starting application with PostgreSQL backend..."
    print_info "Database URL: $db_url"
    
    if [[ "$QUIET" != "true" ]]; then
        echo
        echo "Command: $cmd"
        echo
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_info "[DRY RUN] Would execute: $cmd"
        return 0
    fi
    
    # Execute the command
    eval "$cmd"
}

# Main function
main() {
    # Default values
    local database_name="$DEFAULT_DB_NAME"
    local database_url=""
    local setup_mode=""
    local fallback_mode="false"
    local log_level=""
    local additional_args=""
    
    # Global flags
    QUIET="false"
    DRY_RUN="false"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -v|--version)
                show_version
                exit 0
                ;;
            -d|--database)
                database_name="$2"
                shift 2
                ;;
            -u|--url)
                database_url="$2"
                shift 2
                ;;
            -s|--setup)
                setup_mode="full"
                shift
                ;;
            -i|--init-only)
                setup_mode="init"
                shift
                ;;
            -a|--admin-only)
                setup_mode="admin"
                shift
                ;;
            -f|--fallback)
                fallback_mode="true"
                shift
                ;;
            -q|--quiet)
                QUIET="true"
                shift
                ;;
            --debug)
                log_level="DEBUG"
                shift
                ;;
            --dry-run)
                DRY_RUN="true"
                shift
                ;;
            --)
                shift
                additional_args="$*"
                break
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Set database URL if not provided
    if [[ -z "$database_url" ]]; then
        if [[ -n "$DATABASE_URL" ]]; then
            database_url="$DATABASE_URL"
        else
            database_url="postgresql:///$database_name"
        fi
    fi
    
    # Show header unless quiet
    if [[ "$QUIET" != "true" ]]; then
        print_header "$SCRIPT_NAME v$VERSION"
        echo
    fi
    
    # Check for API key
    if [[ -z "$OPENAI_API_KEY" && "$setup_mode" != "init" && "$setup_mode" != "admin" ]]; then
        print_error "OPENAI_API_KEY environment variable is required"
        print_error "Set it in your .env file or export it before running this script"
        exit 1
    fi
    
    # Setup PostgreSQL environment
    if ! setup_postgresql "$database_name" "$database_url"; then
        print_error "PostgreSQL setup failed"
        if [[ "$fallback_mode" == "true" ]]; then
            print_warning "Fallback mode enabled - you can try running with --db-backend memory"
        fi
        exit 1
    fi
    
    # Handle setup modes
    case "$setup_mode" in
        "full")
            if ! run_database_init "$database_url" "$fallback_mode"; then
                exit 1
            fi
            if ! run_admin_setup "$database_url" "$fallback_mode"; then
                exit 1
            fi
            print_success "Database setup completed successfully!"
            exit 0
            ;;
        "init")
            if ! run_database_init "$database_url" "$fallback_mode"; then
                exit 1
            fi
            print_success "Database initialization completed!"
            exit 0
            ;;
        "admin")
            if ! run_admin_setup "$database_url" "$fallback_mode"; then
                exit 1
            fi
            print_success "Admin user setup completed!"
            exit 0
            ;;
    esac
    
    # Start the application
    start_application "$database_url" "$fallback_mode" "$additional_args" "$log_level"
}

# Run main function with all arguments
main "$@"
