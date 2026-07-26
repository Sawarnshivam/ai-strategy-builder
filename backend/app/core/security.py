"""Password hashing and JWT token helpers.

Isolated from the service layer so the crypto choices live in one place and can
be swapped (e.g. argon2) without touching business logic.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import Settings
from app.core.exceptions import AuthError

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of the plaintext password."""
    return str(_pwd_context.hash(plain))


def verify_password(plain: str, hashed: str) -> bool:
    """Check a plaintext password against its stored hash."""
    return bool(_pwd_context.verify(plain, hashed))


def create_access_token(subject: str, settings: Settings) -> str:
    """Create a signed JWT whose subject is the user id."""
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    return str(jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm))


def decode_access_token(token: str, settings: Settings) -> str:
    """Decode a JWT and return its subject, or raise AuthError."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except (JWTError, ValueError) as exc:
        raise AuthError("Invalid or expired token.") from exc
    subject = payload.get("sub")
    if not isinstance(subject, str):
        raise AuthError("Malformed token.")
    return subject