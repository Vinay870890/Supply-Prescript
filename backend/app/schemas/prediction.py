from pydantic import BaseModel, Field


class ShipmentPredictionRequest(BaseModel):
    shipment_id: int = Field(gt=0)
    country: str

    shipment_mode: str = Field(
        alias="shipment mode"
    )

    product_group: str = Field(
        alias="product group"
    )

    sub_classification: str = Field(
        alias="sub classification"
    )

    vendor: str

    manufacturing_site: str = Field(
        alias="manufacturing site"
    )

    line_item_quantity: float = Field(
        alias="line item quantity",
        ge=0,
    )

    line_item_value: float = Field(
        alias="line item value",
        ge=0,
    )

    pack_price: float = Field(
        alias="pack price",
        ge=0,
    )

    unit_price: float = Field(
        alias="unit price",
        ge=0,
    )

    weight_kg: float = Field(
        alias="weight (kilograms)",
        ge=0,
    )

    freight_cost_usd: float = Field(
        alias="freight cost (usd)",
        ge=0,
    )

    insurance_usd: float = Field(
        alias="line item insurance (usd)",
        ge=0,
    )

    scheduled_year: int

    scheduled_month: int = Field(
        ge=1,
        le=12,
    )

    scheduled_day_of_week: int = Field(
        ge=0,
        le=6,
    )

    freight_cost_ratio: float = Field(
        ge=0,
    )

    insurance_cost_ratio: float = Field(
        ge=0,
    )

    weight_per_unit: float = Field(
        ge=0,
    )

    transport_risk_score: float = Field(
        ge=0,
        le=1,
    )

    high_value_shipment: int = Field(
        ge=0,
        le=1,
    )

    shipment_complexity_score: float = Field(
        ge=0,
    )

    class Config:
        populate_by_name = True