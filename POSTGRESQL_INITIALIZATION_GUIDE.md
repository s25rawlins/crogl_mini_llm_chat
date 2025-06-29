# PostgreSQL Initialization Guide

This guide explains the enhanced PostgreSQL initialization system implemented in Mini LLM Chat, which ensures robust database setup and provides clear error handling.

## Overview

The enhanced PostgreSQL initialization system performs comprehensive checks and automatic setup when using `mini-llm-chat --db-backend postgresql`. The system follows a multi-step approach to ensure PostgreSQL is ready for use.

## Initialization Flow

When you run `mini-llm-chat --db-backend postgresql`, the system performs the following checks in order:

### 1. PostgreSQL Installation Check
- Verifies PostgreSQL is installed on the system
- Checks for `psql` and `pg_config` commands
- Retrieves PostgreSQL version information

### 2. PostgreSQL Service Check
- Verifies PostgreSQL service is running
- Uses `pg_isready` for the most reliable check
- Falls back to platform-specific service checks:
  - **Linux**: `systemctl is-active postgresql` or `service postgresql status`
  - **macOS**: `brew services list` or `launchctl list`
  - **Windows**: `sc query postgresql`

### 3. PostgreSQL Service Start (if needed)
- Attempts to start PostgreSQL service if it's not running
- Platform-specific start commands:
  - **Linux**: `sudo systemctl start postgresql` or `sudo service postgresql start`
  - **macOS**: `brew services start postgresql`
  - **Windows**: `net start postgresql`

### 4. Database Existence Check
- Checks if the target database exists
- Connects to the `postgres` database to query `pg_database`

### 5. Database Creation (if needed)
- Creates the target database if it doesn't exist
- Uses safe SQL identifiers to prevent injection

### 6. Connection Test
- Performs a final connection test to ensure everything works
- Verifies the application can connect to the database

### 7. Database Schema Initialization
- Creates required tables if they don't exist
- Sets up the database schema for the application

### 8. Admin User Check
- Checks if admin users exist in the database
- Prompts for admin user creation if none exist

## Error Handling and Recovery

The system provides specific error messages and recovery suggestions for different failure scenarios:

### PostgreSQL Not Installed
```
============================================================
PostgreSQL Installation Required
============================================================
PostgreSQL is not installed. Please install PostgreSQL and try again.

To resolve this issue:
1. Install PostgreSQL on your system
2. Run the application again
3. Or use in-memory mode: --db-backend memory
============================================================
```

**Installation Commands:**
- **Ubuntu/Debian**: `sudo apt-get install postgresql postgresql-contrib`
- **CentOS/RHEL**: `sudo yum install postgresql-server postgresql-contrib`
- **macOS**: `brew install postgresql`
- **Windows**: Download from https://www.postgresql.org/download/windows/

### PostgreSQL Service Not Running
```
============================================================
PostgreSQL Service Issue
============================================================
PostgreSQL service is not running and could not be started.

To resolve this issue:
1. Start PostgreSQL service manually:
   - Linux: sudo systemctl start postgresql
   - macOS: brew services start postgresql
   - Windows: net start postgresql
2. Run the application again
3. Or use in-memory mode: --db-backend memory
============================================================
```

### Database Does Not Exist
```
============================================================
PostgreSQL Database Issue
============================================================
Target database does not exist and could not be created.

To resolve this issue:
1. Create the database manually:
   createdb mini_llm_chat
2. Check database permissions
3. Verify your DATABASE_URL is correct
4. Or use in-memory mode: --db-backend memory
============================================================
```

### Connection Issues
```
============================================================
PostgreSQL Connection Issue
============================================================
Cannot connect to PostgreSQL database: [specific error]

To resolve this issue:
1. Check your DATABASE_URL is correct
2. Verify PostgreSQL is accepting connections
3. Check authentication credentials
4. Or use in-memory mode: --db-backend memory
============================================================
```

## Command Line Options

### Database Backend Selection
```bash
# Use PostgreSQL (with comprehensive checks)
mini-llm-chat --db-backend postgresql

# Use PostgreSQL with automatic fallback to memory
mini-llm-chat --db-backend postgresql --fallback-to-memory

# Auto-detect (tries PostgreSQL first, falls back to memory)
mini-llm-chat --db-backend auto

# Use in-memory only
mini-llm-chat --db-backend memory
```

### Database URL Configuration
```bash
# Specify custom database URL
mini-llm-chat --db-backend postgresql --database-url postgresql://user:pass@localhost:5432/mydb

# Use environment variable
export DATABASE_URL="postgresql://user:pass@localhost:5432/mydb"
mini-llm-chat --db-backend postgresql
```

### Database Setup Commands
```bash
# Initialize database tables only
mini-llm-chat --init-db --db-backend postgresql

# Set up admin user only
mini-llm-chat --setup-admin --db-backend postgresql
```

## Environment Variables

The system supports the following environment variables:

- `DATABASE_URL`: PostgreSQL connection URL
- `DB_BACKEND`: Default database backend (`postgresql`, `memory`, or `auto`)

Example `.env` file:
```env
DATABASE_URL=postgresql://localhost:5432/mini_llm_chat
DB_BACKEND=postgresql
```

## Fallback Behavior

The system provides multiple fallback mechanisms:

### Automatic Fallback
When using `--fallback-to-memory` or `--db-backend auto`, the system automatically falls back to in-memory mode if PostgreSQL initialization fails.

### Interactive Fallback
When PostgreSQL fails without automatic fallback, the system prompts:
```
PostgreSQL database is not available. Would you like to use in-memory mode instead?
Note: In-memory mode has limited functionality and no data persistence.
Continue with in-memory mode? (y/N):
```

## Troubleshooting

### Common Issues and Solutions

1. **Permission Denied Errors**
   - Ensure your user has permission to connect to PostgreSQL
   - Check `pg_hba.conf` configuration
   - Verify database user credentials

2. **Database Connection Refused**
   - Ensure PostgreSQL is running: `sudo systemctl status postgresql`
   - Check if PostgreSQL is listening on the correct port: `netstat -an | grep 5432`
   - Verify firewall settings

3. **Authentication Failed**
   - Check username and password in DATABASE_URL
   - Verify user exists in PostgreSQL: `psql -c "\du"`
   - Check authentication method in `pg_hba.conf`

4. **Database Does Not Exist**
   - Create database manually: `createdb mini_llm_chat`
   - Ensure user has CREATEDB privilege
   - Check database name in DATABASE_URL

### Debug Mode

For detailed troubleshooting, use debug logging:
```bash
mini-llm-chat --db-backend postgresql --log-level DEBUG
```

This provides detailed information about each step of the initialization process.

## Testing the System

You can test the PostgreSQL initialization system using the provided test script:

```bash
python test_postgresql_initialization.py
```

This script tests:
- PostgreSQL installation detection
- Service status checking
- Database URL parsing
- System readiness verification
- Backend initialization

## Architecture

The enhanced PostgreSQL initialization system consists of:

### Core Components

1. **`postgresql_utils.py`**: System-level PostgreSQL utilities
   - Installation detection
   - Service management
   - Database operations
   - Cross-platform compatibility

2. **Enhanced `PostgreSQLBackend`**: Database backend with system checks
   - Comprehensive initialization
   - Error handling and recovery
   - Integration with utilities

3. **Updated `DatabaseManager`**: High-level database management
   - Backend selection logic
   - Fallback mechanisms
   - Error propagation

4. **Enhanced CLI**: User-friendly command-line interface
   - Clear error messages
   - Recovery suggestions
   - Interactive prompts

### Key Features

- **Cross-platform compatibility**: Works on Linux, macOS, and Windows
- **Comprehensive error handling**: Specific messages for different failure types
- **Automatic recovery**: Attempts to resolve issues automatically
- **Graceful fallback**: Falls back to in-memory mode when needed
- **User-friendly interface**: Clear instructions and suggestions

## Best Practices

1. **Use environment variables** for sensitive configuration like DATABASE_URL
2. **Test your setup** with `--init-db` before running the full application
3. **Use debug logging** when troubleshooting connection issues
4. **Set up proper authentication** in PostgreSQL for security
5. **Use automatic fallback** in development environments
6. **Monitor logs** for security and performance insights

## Security Considerations

- Database URLs in logs are sanitized to hide credentials
- Authentication errors are logged but credentials are redacted
- The system follows PostgreSQL security best practices
- Admin user creation is prompted interactively for security

This enhanced initialization system ensures that PostgreSQL setup is as smooth and error-free as possible, while providing clear guidance when issues occur.
