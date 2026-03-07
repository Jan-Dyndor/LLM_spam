from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"  # type: ignore

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)

    spam: Mapped[list[Predictions]] = relationship(back_populates="user")  # noqa: F821


class Predictions(Base):
    __tablename__ = "predictions"  # type: ignore
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    model_name: Mapped[str] = mapped_column(String, nullable=False)
    input_text: Mapped[str] = mapped_column(String, nullable=False)
    label: Mapped[str] = mapped_column(String(4), nullable=False)
    confidence: Mapped[float] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    prompt_version: Mapped[str] = mapped_column(String, nullable=False)
    is_spam_by_use: Mapped[str] = mapped_column(String, nullable=True)
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(tz=UTC)
    )

    user: Mapped[User] = relationship(back_populates="spam")
