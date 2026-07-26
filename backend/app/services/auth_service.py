"""Authentication business logic: signup, login, and user lookup."""

import uuid

from sqlalchemy.exc import IntegrityError

from app.core.config import Settings
from app.core.exceptions import AuthError, ConflictError
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, SignupRequest

logger = get_logger(__name__)


class AuthService:
    """Coordinates user registration and authentication."""

    def __init__(self, repository: UserRepository, settings: Settings) -> None:
        self._repo = repository
        self._settings = settings

    def signup(self, payload: SignupRequest) -> tuple[User, str]:
        """Register a user and return the user plus an access token."""
        if self._repo.get_by_email(payload.email) is not None:
            raise ConflictError("An account with that email already exists.")

        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
        )
        try:
            self._repo.add(user)
            self._repo.db.commit()
        except IntegrityError as exc:
            self._repo.db.rollback()
            raise ConflictError("An account with that email already exists.") from exc

        self._repo.db.refresh(user)
        logger.info("Registered user %s", user.id)
        return user, create_access_token(str(user.id), self._settings)

    def login(self, payload: LoginRequest) -> str:
        """Authenticate a user and return an access token."""
        user = self._repo.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise AuthError("Incorrect email or password.")
        logger.info("User %s logged in", user.id)
        return create_access_token(str(user.id), self._settings)

    def get_user(self, user_id: uuid.UUID) -> User:
        """Return a user by id or raise AuthError."""
        user = self._repo.get(user_id)
        if user is None:
            raise AuthError("User no longer exists.")
        return user