from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    shipment_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    predicted_delay_probability: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    predicted_risk_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    recommended_action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    selected_action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    recommendation_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    estimated_cost_usd: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    expected_delay_risk: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    decision_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="SELECTED",
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    executed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    execution_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )