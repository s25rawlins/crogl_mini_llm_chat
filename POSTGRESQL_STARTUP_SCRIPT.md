# PostgreSQL Startup Script

This document describes the enhanced PostgreSQL startup script (`start_postgresql.sh`) for Mini LLM Chat.

## Overview

The `start_postgresql.sh` script provides a comprehensive way to run Mini LLM Chat with PostgreSQL backend, including automatic environment setup, error handling, and user-friendly output.

## Features

- **Comprehensive PostgreSQL Setup**: Automatically checks and sets up PostgreSQL environment
- **Cross-Platform Support**: Works on Linux, macOS, and Windows (with appropriate shell)
- **Error Handling**: Provides clear error messages and recovery suggestions
- **Flexible Configuration**: Supports custom database names, URLs, and additional CLI arguments
- **Setup Modes**: Can initialize database and setup admin users
- **Fallback Support**: Optional fallback to memory mode if PostgreSQL fails
- **Colored Output**: User-friendly colored terminal output
- **Dry Run Mode**: Test what would be executed without actually running

## Quick Start

### Basic Usage
```bash
# Start with default settings
./start_postgresql.sh

# Start with setup (initialize database and create admin user)
./start_postgresql.sh --setup
```

### Common Use Cases
```bash
# Initialize database only
./start_postgresql.sh --init-only

# Setup admin user only
./start_postgresql.sh --admin-only

# Use custom database name
./start_postgresql.sh --database myapp

# Use custom database URL
./start_postgresql.sh --url postgresql://user:pass@host:5432/mydb

# Enable fallback to memory mode
./start_postgresql.sh --fallback

# Pass additional CLI arguments
./start_postgresql.sh -- --max-calls 10 --time-window 300

# Debug mode
./start_postgresql.sh --debug

# Quiet mode (suppress non-error output)
./start_postgresql.sh --quiet

# Dry run (show what would be executed)
./start_postgresql.sh --dry-run
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `-h, --help` | Show help message |
| `-v, --version` | Show version information |
| `-d, --database NAME` | Database name (default: mini_llm_chat) |
| `-u, --url URL` | Custom database URL |
| `-s, --setup` | Run database setup (init-db and setup-admin) |
| `-i, --init-only` | Initialize database tables only |
| `-a, --admin-only` | Setup admin user only |
| `-f, --fallback` | Enable fallback to memory mode |
| `-q, --quiet` | Suppress non-error output |
| `--debug` | Enable debug logging |
| `--dry-run` | Show what would be executed without running |
| `-- ARGS` | Pass additional arguments to CLI |

## Environment Variables

The script respects the following environment variables:

- `DATABASE_URL`: PostgreSQL connection URL
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `DB_BACKEND`: Database backend preference
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Setup Process

The script performs the following steps automatically:

1. **PostgreSQL Installation Check**: Verifies PostgreSQL is installed
2. **Service Status Check**: Checks if PostgreSQL service is running
3. **Service Start**: Attempts to start PostgreSQL if not running
4. **Database Check**: Verifies target database exists
5. **Database Creation**: Creates database if it doesn't exist
6. **Connection Test**: Tests database connectivity
7. **Application Launch**: Starts Mini LLM Chat with PostgreSQL backend

## Error Handling

The script provides specific error messages and recovery suggestions for common issues:

### PostgreSQL Not Installed
```
[ERROR] PostgreSQL client (psql) not found
[ERROR] Please install PostgreSQL and try again

Installation commands:
  Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib
  CentOS/RHEL:   sudo yum install postgresql-server postgresql-contrib
  macOS:         brew install postgresql
  Windows:       Download from https://www.postgresql.org/download/
```

### Service Not Running
```
[WARNING] PostgreSQL service is not running
[INFO] Attempting to start PostgreSQL service...
[INFO] Starting PostgreSQL with systemctl...
[SUCCESS] PostgreSQL service started
```

### Database Issues
```
[WARNING] Database 'mini_llm_chat' does not exist
[INFO] Creating database 'mini_llm_chat'...
[SUCCESS] Database 'mini_llm_chat' created successfully
```

## Examples

### First-Time Setup
```bash
# Complete setup for new installation
./start_postgresql.sh --setup
```

This will:
1. Check PostgreSQL installation and service
2. Create database if needed
3. Initialize database tables
4. Setup admin user
5. Start the application

### Development Workflow
```bash
# Start with fallback for development
./start_postgresql.sh --fallback --debug
```

### Production Deployment
```bash
# Use specific database URL
./start_postgresql.sh --url postgresql://user:pass@prod-server:5432/mini_llm_chat --quiet
```

### Testing Configuration
```bash
# Dry run to see what would be executed
./start_postgresql.sh --setup --dry-run
```

## Comparison with Original Script

| Feature | `run_with_postgresql.sh` | `start_postgresql.sh` |
|---------|-------------------------|----------------------|
| PostgreSQL Setup | Manual | Automatic |
| Error Handling | Basic | Comprehensive |
| Service Management | None | Automatic |
| Database Creation | Manual | Automatic |
| User Guidance | Minimal | Extensive |
| Setup Options | None | Multiple modes |
| Colored Output | No | Yes |
| Cross-Platform | Limited | Full |
| Dry Run Mode | No | Yes |
| Fallback Support | No | Yes |

## Troubleshooting

### Permission Issues
If you encounter permission errors:
```bash
# Make script executable
chmod +x start_postgresql.sh

# For PostgreSQL service start issues
sudo systemctl start postgresql
```

### Database Connection Issues
```bash
# Test connection manually
psql -d mini_llm_chat -c "SELECT 1;"

# Check PostgreSQL status
pg_isready
```

### Environment Issues
```bash
# Check environment variables
echo $DATABASE_URL
echo $OPENAI_API_KEY

# Load from .env file
source .env
```

## Integration

The script integrates seamlessly with the existing Mini LLM Chat infrastructure:

- Uses the same CLI interface and arguments
- Respects all environment variables
- Compatible with existing configuration files
- Works with the enhanced PostgreSQL backend system

## Security Considerations

- Database URLs in output are sanitized to hide credentials
- API keys are checked but not displayed in logs
- Admin user creation is handled securely
- Service operations use appropriate permissions

## Future Enhancements

Potential improvements for future versions:

- Configuration file support
- Docker integration
- Backup and restore functionality
- Health check endpoints
- Monitoring integration
- Multi-database support

## Support

For issues or questions:

1. Check the error messages and suggested solutions
2. Review the PostgreSQL Initialization Guide
3. Use `--debug` mode for detailed logging
4. Use `--dry-run` to test configuration
5. Refer to the main project documentation

The script is designed to be self-documenting with comprehensive help text and clear error messages.
