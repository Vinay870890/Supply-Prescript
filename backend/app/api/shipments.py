from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter(
    prefix="/api/shipments",
    tags=["Shipments"],
)


@router.get("")
def get_shipments(
    limit: int = 50,
    offset: int = 0,
    search: str | None = None,
    risk: str | None = None,
    shipment_mode: str | None = None,
    db: Session = Depends(get_db),
):
    limit = min(max(limit, 1), 200)
    offset = max(offset, 0)

    conditions = []
    params = {
        "limit": limit,
        "offset": offset,
    }

    if search:
        conditions.append(
            "CAST(id AS TEXT) ILIKE :search"
        )
        params["search"] = f"%{search}%"

    if shipment_mode:
        conditions.append(
            '"shipment mode" ILIKE :shipment_mode'
        )
        params["shipment_mode"] = shipment_mode

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = text(
        f"""
        SELECT
            id,
            country,
            "shipment mode",
            "product group",
            vendor,
            "line item quantity",
            "line item value",
            "weight (kilograms)",
            "freight cost (usd)",
            "actual_delay_days",
            "delay_flag",
            "transport_risk_score",
            "high_value_shipment",
            "shipment_complexity_score"
        FROM shipments
        {where_clause}
        ORDER BY id
        LIMIT :limit
        OFFSET :offset
        """
    )

    rows = db.execute(query, params).mappings().all()

    return {
        "count": len(rows),
        "limit": limit,
        "offset": offset,
        "results": [dict(row) for row in rows],
    }


@router.get("/{shipment_id}")
def get_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
):
    query = text(
        """
        SELECT *
        FROM shipments
        WHERE id = :shipment_id
        """
    )

    row = db.execute(
        query,
        {"shipment_id": shipment_id},
    ).mappings().first()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Shipment not found",
        )

    return dict(row)