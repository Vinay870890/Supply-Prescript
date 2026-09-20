from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    project_code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    vendor: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    product_group: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    shipment_mode: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    line_item_quantity: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    line_item_value: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    freight_cost_usd: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    actual_delay_days: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    delay_flag: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    shipment_value_usd: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )