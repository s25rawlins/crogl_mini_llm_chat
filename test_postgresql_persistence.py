#!/usr/bin/env python3
"""
Test script to verify PostgreSQL conversation persistence across sessions.

This script tests whether conversations and messages are properly stored
and retrieved from PostgreSQL database across different application sessions.
"""

import os
import sys
import time
from datetime import datetime
from typing import Optional

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mini_llm_chat.backends.postgresql import PostgreSQLBackend
from mini_llm_chat.database_manager import initialize_database


def test_postgresql_persistence():
    """Test PostgreSQL persistence across simulated sessions."""
    print("Testing PostgreSQL conversation persistence across sessions...")
    print("=" * 60)
    
    # Test configuration
    test_username = "test_user_persistence"
    test_email = "test@persistence.com"
    test_password = "test_password_123"
    conversation_title = f"Test Conversation {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    try:
        # Session 1: Create user, conversation, and messages
        print("\n[SESSION 1] Creating user, conversation, and messages...")
        
        backend1 = initialize_database(
            backend_type="postgresql",
            fallback_to_memory=False,
            interactive_fallback=False
        )
        
        # Initialize database tables
        backend1.init_db()
        
        # Create test user
        user_created = backend1.create_admin_user(test_username, test_email, test_password)
        if user_created:
            print(f"+ Created test user: {test_username}")
        else:
            print(f"i Test user already exists: {test_username}")
        
        # Authenticate user
        user = backend1.authenticate_user(test_username, test_password)
        if not user:
            print("- Failed to authenticate test user")
            return False
        print(f"+ Authenticated user: {user.username} (ID: {user.id})")
        
        # Create conversation
        conversation = backend1.create_conversation(user.id, conversation_title)
        if not conversation:
            print("- Failed to create conversation")
            return False
        print(f"+ Created conversation: '{conversation.title}' (ID: {conversation.id})")
        
        # Add test messages
        test_messages = [
            ("system", "You are a helpful assistant.", 10),
            ("user", "Hello, this is a test message for persistence.", 15),
            ("assistant", "Hello! I understand this is a test for PostgreSQL persistence.", 20),
            ("user", "Can you remember this conversation across sessions?", 12),
            ("assistant", "Yes, if PostgreSQL persistence is working correctly, this conversation should be remembered.", 25),
        ]
        
        message_ids = []
        for role, content, token_count in test_messages:
            message = backend1.add_message(conversation.id, role, content, token_count)
            if message:
                message_ids.append(message.id)
                print(f"+ Added {role} message: '{content[:50]}...' (ID: {message.id})")
            else:
                print(f"- Failed to add {role} message")
                return False
        
        print(f"\n+ Session 1 completed. Created {len(message_ids)} messages in conversation {conversation.id}")
        
        # Simulate session end
        print("\n[SIMULATING] Session 1 ended, database connection closed...")
        time.sleep(1)
        
        # Session 2: Reconnect and verify data persistence
        print("\n[SESSION 2] Reconnecting and verifying data persistence...")
        
        backend2 = initialize_database(
            backend_type="postgresql",
            fallback_to_memory=False,
            interactive_fallback=False
        )
        
        # Re-authenticate user
        user2 = backend2.authenticate_user(test_username, test_password)
        if not user2:
            print("- Failed to re-authenticate user in session 2")
            return False
        print(f"+ Re-authenticated user: {user2.username} (ID: {user2.id})")
        
        # Verify user data persistence
        if user.id != user2.id or user.username != user2.username:
            print("- User data not consistent across sessions")
            return False
        print("+ User data consistent across sessions")
        
        # Retrieve conversation messages
        messages = backend2.get_conversation_messages(conversation.id)
        if not messages:
            print("- No messages retrieved from conversation")
            return False
        
        print(f"+ Retrieved {len(messages)} messages from conversation {conversation.id}")
        
        # Verify message content and order
        if len(messages) != len(test_messages):
            print(f"- Message count mismatch: expected {len(test_messages)}, got {len(messages)}")
            return False
        
        for i, (expected_role, expected_content, expected_tokens) in enumerate(test_messages):
            message = messages[i]
            if (message.role != expected_role or 
                message.content != expected_content or 
                message.token_count != expected_tokens):
                print(f"- Message {i} content mismatch:")
                print(f"   Expected: {expected_role} | {expected_content} | {expected_tokens}")
                print(f"   Got:      {message.role} | {message.content} | {message.token_count}")
                return False
            print(f"+ Message {i} verified: {message.role} | '{message.content[:30]}...'")
        
        # Test adding new message in session 2
        new_message = backend2.add_message(
            conversation.id, 
            "user", 
            "This message was added in session 2 to test persistence.", 
            18
        )
        if not new_message:
            print("- Failed to add new message in session 2")
            return False
        print(f"+ Added new message in session 2 (ID: {new_message.id})")
        
        # Session 3: Final verification
        print("\n[SESSION 3] Final verification of all data...")
        
        backend3 = initialize_database(
            backend_type="postgresql",
            fallback_to_memory=False,
            interactive_fallback=False
        )
        
        # Verify all messages including the new one
        all_messages = backend3.get_conversation_messages(conversation.id)
        expected_total = len(test_messages) + 1  # Original messages + new message
        
        if len(all_messages) != expected_total:
            print(f"- Final message count incorrect: expected {expected_total}, got {len(all_messages)}")
            return False
        
        print(f"+ Final verification: {len(all_messages)} messages persisted correctly")
        
        # Verify the new message is there
        last_message = all_messages[-1]
        if (last_message.role != "user" or 
            "session 2" not in last_message.content):
            print("- New message from session 2 not found or incorrect")
            return False
        print("+ New message from session 2 verified")
        
        print("\n" + "=" * 60)
        print("SUCCESS: PostgreSQL persistence test PASSED!")
        print("* User authentication persists across sessions")
        print("* Conversation data persists across sessions")
        print("* Message content and order preserved")
        print("* New messages can be added in subsequent sessions")
        print("* All data remains consistent across multiple reconnections")
        
        return True
        
    except Exception as e:
        print(f"\n- ERROR during persistence test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_backend_comparison():
    """Test memory backend to show the difference in persistence."""
    print("\n" + "=" * 60)
    print("COMPARISON: Testing memory backend (should NOT persist)")
    print("=" * 60)
    
    try:
        # Session 1 with memory backend
        print("\n[MEMORY SESSION 1] Creating data in memory backend...")
        
        backend1 = initialize_database(
            backend_type="memory",
            fallback_to_memory=True,
            interactive_fallback=False
        )
        
        backend1.init_db()
        
        # Get session user (memory backend creates a default session user)
        if hasattr(backend1, 'get_session_user'):
            session_user = backend1.get_session_user()
        else:
            # For backends without get_session_user, try to authenticate with session_user
            session_user = backend1.authenticate_user("session_user", "anypassword")
        
        if not session_user:
            print("- No session user found in memory backend")
            return False
        
        # Create conversation
        conversation = backend1.create_conversation(session_user.id, "Memory Test Conversation")
        if not conversation:
            print("- Failed to create conversation in memory backend")
            return False
        
        # Add message
        message = backend1.add_message(conversation.id, "user", "This is in memory only", 10)
        if not message:
            print("- Failed to add message in memory backend")
            return False
        
        print(f"+ Created conversation {conversation.id} with message in memory backend")
        
        # Session 2 with new memory backend instance
        print("\n[MEMORY SESSION 2] Creating new memory backend instance...")
        
        backend2 = initialize_database(
            backend_type="memory",
            fallback_to_memory=True,
            interactive_fallback=False
        )
        
        backend2.init_db()
        
        # Try to retrieve the conversation (should fail)
        messages = backend2.get_conversation_messages(conversation.id)
        
        if messages:
            print("- UNEXPECTED: Memory backend persisted data across instances!")
            return False
        else:
            print("+ EXPECTED: Memory backend did NOT persist data (conversation lost)")
        
        print("\n+ Memory backend comparison completed")
        print("  - Memory backend: Data lost between sessions (as expected)")
        print("  - PostgreSQL backend: Data persists between sessions")
        
        return True
        
    except Exception as e:
        print(f"\n- ERROR during memory backend test: {e}")
        return False


def main():
    """Main test function."""
    print("PostgreSQL Persistence Test Suite")
    print("=" * 60)
    print("This script tests whether PostgreSQL properly persists")
    print("conversations and messages across application sessions.")
    print()
    
    # Check if PostgreSQL backend is available
    try:
        backend = initialize_database(
            backend_type="postgresql",
            fallback_to_memory=False,
            interactive_fallback=False
        )
        backend_info = backend.get_backend_info()
        print(f"+ PostgreSQL backend available: {backend_info['name']}")
        print(f"  Database URL: {backend_info.get('database_url', 'Not specified')}")
    except Exception as e:
        print(f"- PostgreSQL backend not available: {e}")
        print("\nPlease ensure:")
        print("1. PostgreSQL is installed and running")
        print("2. Database 'mini_llm_chat' exists")
        print("3. DATABASE_URL environment variable is set correctly")
        sys.exit(1)
    
    # Run tests
    success = True
    
    # Test PostgreSQL persistence
    if not test_postgresql_persistence():
        success = False
    
    # Test memory backend for comparison
    if not test_memory_backend_comparison():
        success = False
    
    # Final result
    print("\n" + "=" * 60)
    if success:
        print("ALL TESTS PASSED!")
        print("PostgreSQL persistence is working correctly.")
    else:
        print("SOME TESTS FAILED!")
        print("PostgreSQL persistence may not be working correctly.")
    
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
