import logging
from typing import Optional

from .backends import DatabaseBackend, InMemoryBackend, PostgreSQLBackend

logger = logging.getLogger(__name__)


class DatabaseConnectionError(Exception):
    pass


class DatabaseManager:
    def __init__(self, backend: Optional[DatabaseBackend] = None):
        self.backend = backend
        self._initialized = False

    def initialize_backend(
        self,
        backend_type: str = "auto",
        fallback_to_memory: bool = False,
        database_url: Optional[str] = None,
    ) -> DatabaseBackend:
        if self.backend and self._initialized:
            return self.backend

        if backend_type == "memory":
            logger.info("Initializing in-memory database backend")
            self.backend = InMemoryBackend()
        elif backend_type == "postgresql":
            logger.info("Initializing PostgreSQL database backend")
            try:
                self.backend = PostgreSQLBackend(database_url)
                # Perform comprehensive PostgreSQL system checks
                self.backend.ensure_postgresql_system_ready()
            except Exception as e:
                if fallback_to_memory:
                    logger.warning(f"PostgreSQL initialization failed: {e}")
                    logger.info("Falling back to in-memory backend")
                    self.backend = InMemoryBackend()
                else:
                    raise DatabaseConnectionError(
                        f"PostgreSQL initialization failed: {e}"
                    )
        elif backend_type == "auto":
            # Try PostgreSQL first, fallback to memory
            try:
                logger.info(
                    "Auto-detecting database backend (trying PostgreSQL first)"
                )
                self.backend = PostgreSQLBackend(database_url)
                # Perform comprehensive PostgreSQL system checks
                self.backend.ensure_postgresql_system_ready()
                logger.info("Successfully initialized PostgreSQL backend")
            except Exception as e:
                logger.warning(f"PostgreSQL not available: {e}")
                logger.info("Using in-memory backend")
                self.backend = InMemoryBackend()
        else:
            raise ValueError(f"Unknown backend type: {backend_type}")

        # Initialize the backend
        try:
            # For PostgreSQL backends, use smart initialization
            if hasattr(self.backend, "ensure_database_ready"):
                admin_needed = not self.backend.ensure_database_ready()
                if admin_needed:
                    logger.info("Database ready but no admin users found")
                    # We'll handle admin user creation in the CLI
            else:
                # For other backends, use traditional initialization
                self.backend.init_db()

            self._initialized = True
            backend_name = self.backend.get_backend_info()["name"]
            logger.info(f"Database backend initialized: {backend_name}")
            return self.backend
        except Exception as e:
            raise DatabaseConnectionError(f"Backend initialization failed: {e}")

    def get_backend(self) -> DatabaseBackend:
        if not self.backend or not self._initialized:
            raise RuntimeError("Database backend not initialized")
        return self.backend

    def get_backend_info(self) -> dict:
        if not self.backend:
            return {"name": "None", "initialized": False}

        info = self.backend.get_backend_info()
        info["initialized"] = self._initialized
        return info

    def supports_persistence(self) -> bool:
        if not self.backend:
            return False
        return self.backend.supports_persistence()

    def prompt_for_fallback(self) -> bool:
        try:
            response = (
                input(
                    "PostgreSQL database is not available. Would you like to use in-memory mode instead?\n"
                    "Note: In-memory mode has limited functionality and no data persistence.\n"
                    "Continue with in-memory mode? (y/N): "
                )
                .strip()
                .lower()
            )
            return response in ["y", "yes"]
        except (EOFError, KeyboardInterrupt):
            return False


_db_manager = DatabaseManager()


def get_database_manager() -> DatabaseManager:
    return _db_manager


def initialize_database(
    backend_type: str = "auto",
    fallback_to_memory: bool = False,
    database_url: Optional[str] = None,
    interactive_fallback: bool = False,
) -> DatabaseBackend:
    manager = get_database_manager()

    try:
        return manager.initialize_backend(
            backend_type, fallback_to_memory, database_url
        )
    except DatabaseConnectionError as e:
        if interactive_fallback and backend_type in ["postgresql", "auto"]:
            if manager.prompt_for_fallback():
                logger.info("User chose to fallback to in-memory mode")
                return manager.initialize_backend("memory", False, database_url)
        raise e


def init_db() -> None:
    backend = get_database_manager().get_backend()
    backend.init_db()


def create_admin_user(username: str, email: str, password: str) -> bool:
    backend = get_database_manager().get_backend()
    return backend.create_admin_user(username, email, password)


def authenticate_user(username: str, password: str):
    backend = get_database_manager().get_backend()
    return backend.authenticate_user(username, password)


def get_user_by_token(token: str):
    backend = get_database_manager().get_backend()
    return backend.get_user_by_token(token)


def create_conversation(user_id: int, title: Optional[str] = None):
    backend = get_database_manager().get_backend()
    return backend.create_conversation(user_id, title)


def add_message(
    conversation_id: int, role: str, content: str, token_count: Optional[int] = None
):
    backend = get_database_manager().get_backend()
    return backend.add_message(conversation_id, role, content, token_count)


def get_conversation_messages(conversation_id: int, limit: Optional[int] = None):
    backend = get_database_manager().get_backend()
    return backend.get_conversation_messages(conversation_id, limit)


def truncate_conversation_messages(conversation_id: int, max_messages: int) -> bool:
    backend = get_database_manager().get_backend()
    return backend.truncate_conversation_messages(conversation_id, max_messages)


def get_session_user():
    backend = get_database_manager().get_backend()
    if hasattr(backend, "get_session_user"):
        return backend.get_session_user()
    return None
