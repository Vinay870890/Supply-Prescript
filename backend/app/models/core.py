from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shipment_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    supplier_id: Mapped[str] = mapped_column(String(50), nullable=False)
    product_category: Mapped[str] = mapped_column(String(100), nullable=False)
    transport_mode: Mapped[str] = mapped_column(String(50), nullable=False)

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    shipment_value: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )