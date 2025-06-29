#!/usr/bin/env python3
"""
Test script for PostgreSQL initialization enhancements.

This script tests the new PostgreSQL system checks and initialization
functionality to ensure it works correctly in various scenarios.
"""

import os
import sys
import logging
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mini_llm_chat.utils.postgresql_utils import (
    is_postgresql_installed,
    get_postgresql_version,
    is_postgresql_service_running,
    get_postgresql_status,
    ensure_postgresql_ready,
    parse_database_url,
)
from mini_llm_chat.backends.postgresql import PostgreSQLBackend
from mini_llm_chat.database_manager import initialize_database, DatabaseConnectionError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)


def test_postgresql_utilities():
    """Test PostgreSQL utility functions."""
    print("="*60)
    print("Testing PostgreSQL Utilities")
    print("="*60)
    
    # Test installation check
    print(f"PostgreSQL installed: {is_postgresql_installed()}")
    
    # Test version check
    version = get_postgresql_version()
    print(f"PostgreSQL version: {version or 'Not available'}")
    
    # Test service status
    print(f"PostgreSQL service running: {is_postgresql_service_running()}")
    
    # Test comprehensive status
    status = get_postgresql_status()
    print(f"PostgreSQL status: {status}")
    
    print()


def test_database_url_parsing():
    """Test database URL parsing."""
    print("="*60)
    print("Testing Database URL Parsing")
    print("="*60)
    
    test_urls = [
        "postgresql://localhost:5432/mini_llm_chat",
        "postgresql://user:pass@localhost:5432/testdb",
        "postgresql:///mini_llm_chat",  # Unix socket
        "postgresql://user@localhost/testdb",
    ]
    
    for url in test_urls:
        try:
            parsed = parse_database_url(url)
            print(f"URL: {url}")
            print(f"  Parsed: {parsed}")
        except Exception as e:
            print(f"URL: {url}")
            print(f"  Error: {e}")
        print()


def test_postgresql_readiness():
    """Test PostgreSQL readiness check."""
    print("="*60)
    print("Testing PostgreSQL Readiness")
    print("="*60)
    
    # Test with default database URL
    database_url = os.getenv("DATABASE_URL", "postgresql://localhost:5432/mini_llm_chat_test")
    
    try:
        success, message = ensure_postgresql_ready(database_url)
        print(f"PostgreSQL ready: {success}")
        print(f"Message: {message}")
    except Exception as e:
        print(f"Error during readiness check: {e}")
    
    print()


def test_backend_initialization():
    """Test PostgreSQL backend initialization."""
    print("="*60)
    print("Testing Backend Initialization")
    print("="*60)
    
    # Test with different scenarios
    test_scenarios = [
        ("memory", "In-memory backend"),
        ("postgresql", "PostgreSQL backend"),
        ("auto", "Auto-detection"),
    ]
    
    for backend_type, description in test_scenarios:
        print(f"Testing {description} ({backend_type})...")
        try:
            backend = initialize_database(
                backend_type=backend_type,
                fallback_to_memory=True,
                database_url=os.getenv("DATABASE_URL"),
                interactive_fallback=False,
            )
            
            backend_info = backend.get_backend_info()
            print(f"  Success: {backend_info['name']} ({backend_info['type']})")
            
        except DatabaseConnectionError as e:
            print(f"  Failed: {e}")
        except Exception as e:
            print(f"  Unexpected error: {e}")
        
        print()


def test_postgresql_backend_direct():
    """Test PostgreSQL backend directly."""
    print("="*60)
    print("Testing PostgreSQL Backend Direct")
    print("="*60)
    
    database_url = os.getenv("DATABASE_URL", "postgresql://localhost:5432/mini_llm_chat_test")
    
    try:
        # Create backend instance
        backend = PostgreSQLBackend(database_url)
        print("Backend created successfully")
        
        # Test system readiness
        backend.ensure_postgresql_system_ready()
        print("System readiness check passed")
        
        # Test database readiness
        admin_needed = not backend.ensure_database_ready()
        print(f"Database ready, admin needed: {admin_needed}")
        
        # Get backend info
        info = backend.get_backend_info()
        print(f"Backend info: {info}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print()


def main():
    """Run all tests."""
    print("PostgreSQL Initialization Test Suite")
    print("="*60)
    print()
    
    # Test individual utilities
    test_postgresql_utilities()
    
    # Test URL parsing
    test_database_url_parsing()
    
    # Test readiness check
    test_postgresql_readiness()
    
    # Test backend initialization
    test_backend_initialization()
    
    # Test direct backend usage
    test_postgresql_backend_direct()
    
    print("="*60)
    print("Test suite completed")
    print("="*60)


if __name__ == "__main__":
    main()
