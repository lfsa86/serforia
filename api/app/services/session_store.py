"""
In-memory session store for user authentication data
Stores user info associated with JWT tokens
"""
import time
import threading
from typing import Optional, Dict
from ..models.auth import UserInfo


class SessionStore:
    """
    In-memory session store for mapping tokens to user info

    Features:
    - O(1) lookup by token
    - Automatic cleanup of expired sessions
    - Thread-safe operations
    """

    # Token expiration time in seconds (2 hours, matching SGI)
    TOKEN_EXPIRATION = 2 * 60 * 60

    # Cleanup interval in seconds (every 10 minutes)
    CLEANUP_INTERVAL = 10 * 60

    def __init__(self):
        self._sessions: Dict[str, dict] = {}
        self._lock = threading.Lock()
        self._last_cleanup = time.time()

    def store(self, token: str, user_info: UserInfo) -> None:
        """
        Store user info associated with a token

        Args:
            token: JWT token
            user_info: User information to store
        """
        with self._lock:
            self._sessions[token] = {
                "user": user_info,
                "created_at": time.time()
            }
            self._maybe_cleanup()

    def get(self, token: str) -> Optional[UserInfo]:
        """
        Retrieve user info by token

        Args:
            token: JWT token

        Returns:
            UserInfo if found and not expired, None otherwise
        """
        with self._lock:
            session = self._sessions.get(token)

            if not session:
                return None

            # Check if expired
            if time.time() - session["created_at"] > self.TOKEN_EXPIRATION:
                del self._sessions[token]
                return None

            return session["user"]

    def remove(self, token: str) -> None:
        """
        Remove a session by token (logout)

        Args:
            token: JWT token to remove
        """
        with self._lock:
            self._sessions.pop(token, None)

    def _maybe_cleanup(self) -> None:
        """
        Cleanup expired sessions if cleanup interval has passed
        Called internally, assumes lock is held
        """
        now = time.time()
        if now - self._last_cleanup < self.CLEANUP_INTERVAL:
            return

        self._last_cleanup = now
        expired_tokens = [
            token for token, session in self._sessions.items()
            if now - session["created_at"] > self.TOKEN_EXPIRATION
        ]

        for token in expired_tokens:
            del self._sessions[token]

    def active_sessions_count(self) -> int:
        """
        Get count of active sessions

        Returns:
            Number of active sessions
        """
        with self._lock:
            return len(self._sessions)


# Singleton instance
_session_store: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    """
    Get singleton instance of SessionStore

    Returns:
        SessionStore instance
    """
    global _session_store
    if _session_store is None:
        _session_store = SessionStore()
    return _session_store
