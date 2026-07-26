"""Queries scoped to the User aggregate."""

from sqlalchemy import select

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Read and write access for users."""

    model = User

    def get_by_email(self, email: str) -> User | None:
        """Return a user by email, or None."""
        stmt = select(User).where(User.email == email)
        return self._db.execute(stmt).scalars().first()