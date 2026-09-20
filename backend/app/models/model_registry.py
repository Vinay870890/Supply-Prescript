from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    model_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    model_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="CANDIDATE",
    )

    accuracy: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    precision: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    recall: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    f1_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    roc_auc: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    feature_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )