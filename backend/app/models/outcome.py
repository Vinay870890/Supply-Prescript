from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class DecisionOutcome(Base):
    __tablename__ = "decision_outcomes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    decision_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    shipment_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    actual_delay_days: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    actual_delay_flag: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    actual_cost_usd: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    outcome_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    outcome_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )