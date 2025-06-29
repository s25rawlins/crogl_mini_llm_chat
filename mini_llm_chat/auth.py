import getpass
import logging
import os
from typing import Optional, Tuple

from mini_llm_chat.backends.base import User
from mini_llm_chat.database_manager import (
    authenticate_user,
    create_admin_user,
    get_user_by_token,
)

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    pass


class AuthorizationError(Exception):
    pass


def login_user() -> Tuple[User, str]:
    print("Authentication Required")
    print("=" * 30)

    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        try:
            username = input("Username: ").strip()
            if not username:
                print("Username cannot be empty")
                continue

            password = getpass.getpass("Password: ")
            if not password:
                print("Password cannot be empty")
                continue

            # Authenticate user
            user = authenticate_user(username, password)
            if user:
                token = user.generate_token()
                logger.info(f"User '{username}' logged in successfully")
                print(f"Welcome, {user.username}! (Role: {user.role})")
                return user, token
            else:
                attempts += 1
                remaining = max_attempts - attempts
                if remaining > 0:
                    print(f"Invalid credentials. {remaining} attempts remaining.")
                else:
                    print("Authentication failed. Maximum attempts exceeded.")

        except KeyboardInterrupt:
            print("\nLogin cancelled.")
            raise AuthenticationError("Login cancelled by user")
        except Exception as e:
            logger.error(f"Login error: {e}")
            print(f"Login error: {e}")
            attempts += 1

    raise AuthenticationError("Authentication failed after maximum attempts")


def login_with_token(token: str) -> Optional[User]:
    try:
        user = get_user_by_token(token)
        if user:
            logger.info(f"User '{user.username}' authenticated via token")
            return user
        else:
            logger.warning("Invalid or expired token")
            return None
    except Exception as e:
        logger.error(f"Token authentication error: {e}")
        return None


def require_admin(user: User) -> None:
    if not user.is_admin():
        logger.warning(
            f"User '{user.username}' attempted admin action without privileges"
        )
        raise AuthorizationError("Admin privileges required")


def setup_initial_admin() -> bool:
    print("Initial Setup - Create Admin User")
    print("=" * 40)

    try:
        username = input("Admin username: ").strip()
        if not username:
            print("Username cannot be empty")
            return False

        email = input("Admin email: ").strip()
        if not email:
            print("Email cannot be empty")
            return False

        password = getpass.getpass("Admin password: ")
        if not password:
            print("Password cannot be empty")
            return False

        confirm_password = getpass.getpass("Confirm password: ")
        if password != confirm_password:
            print("Passwords do not match")
            return False

        # Create admin user
        success = create_admin_user(username, email, password)
        if success:
            print(f"Admin user '{username}' created successfully")
            return True
        else:
            print(f"Admin user '{username}' already exists")
            return False

    except KeyboardInterrupt:
        print("\nSetup cancelled.")
        return False
    except Exception as e:
        logger.error(f"Admin setup error: {e}")
        print(f"Setup error: {e}")
        return False


def get_auth_from_env() -> Optional[str]:
    return os.getenv("MINI_LLM_CHAT_TOKEN")


def save_token_to_env_file(token: str, env_file: str = ".env") -> bool:
    try:
        env_vars = {}
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()

        env_vars["MINI_LLM_CHAT_TOKEN"] = token

        with open(env_file, "w") as f:
            f.write("# Mini LLM Chat Environment Variables\n")
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")

        logger.info(f"Token saved to {env_file}")
        return True
    except Exception as e:
        logger.error(f"Failed to save token to env file: {e}")
        return False


def interactive_auth() -> Tuple[User, str]:
    existing_token = get_auth_from_env()
    if existing_token:
        user = login_with_token(existing_token)
        if user:
            print(f"Authenticated as {user.username} (Role: {user.role})")
            return user, existing_token
        else:
            print("Existing token is invalid or expired")

    user, token = login_user()

    save_token = input("\nSave authentication token? (y/N): ").strip().lower()
    if save_token in ["y", "yes"]:
        if save_token_to_env_file(token):
            print("Token saved to .env file")
        else:
            print("Failed to save token")

    return user, token


def check_permissions(user: User, required_role: str = "user") -> bool:
    if required_role == "admin":
        return user.is_admin()
    elif required_role == "user":
        return True
    else:
        logger.warning(f"Unknown role requirement: {required_role}")
        return False


def logout_user(token: str) -> bool:
    try:
        env_file = ".env"
        if os.path.exists(env_file):
            env_vars = {}
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        if key.strip() != "MINI_LLM_CHAT_TOKEN":
                            env_vars[key.strip()] = value.strip()

            with open(env_file, "w") as f:
                f.write("# Mini LLM Chat Environment Variables\n")
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")

        logger.info("User logged out successfully")
        return True
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return False
