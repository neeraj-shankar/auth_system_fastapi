import uuid
from app.database import Base
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column




class User(Base):
    """
    The User ORM model — maps directly to the 'users' table in PostgreSQL.
 
    SQLAlchemy 2.0 uses `Mapped[type]` + `mapped_column()` syntax.
    This is fully type-annotated, so your editor understands the field types.
    The old `Column(String)` style still works but this is the modern way.
    """

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(
        String(236),
        unique=True,
        nullable=False,
        index=True
    )
    hashed_password: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default= lambda: datetime.now(timezone.utc),
        nullable= False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate= lambda: datetime.now(timezone.utc),
        nullable= False
    )

    def __repr__(self) -> str:
        """Developer-friendly string representation. Never exposes password."""
        return f"<User id={self.id!r} email={self.email!r} active={self.is_active}>"