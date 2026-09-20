import json
from pathlib import Path

import requests


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "decision_batch_20.json"
)

API_URL = "http://localhost:8001/api/decision"


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)

    print("=" * 60)
    print("SUPPLY PRESCRIPT - CREATE BATCH DECISIONS")
    print("=" * 60)
    print(f"Loaded {len(records)} shipment records.")
    print()

    success = 0
    failed = 0

    for index, payload in enumerate(records, start=1):

        shipment_id = payload.get("shipment_id")

        if shipment_id is None:
            failed += 1
            print(
                f"[{index:02d}/{len(records)}] "
                f"FAILED | Missing shipment_id"
            )
            continue

        try:
            response = requests.post(
                API_URL,
                json=payload,
                timeout=120,
            )

            if response.ok:
                result = response.json()

                success += 1

                decision_id = (
                    result.get("decision_id", "N/A")
                    if isinstance(result, dict)
                    else "N/A"
                )

                returned_shipment_id = (
                    result.get("shipment_id", shipment_id)
                    if isinstance(result, dict)
                    else shipment_id
                )

                print(
                    f"[{index:02d}/{len(records)}] "
                    f"SUCCESS | "
                    f"Shipment ID: {returned_shipment_id} | "
                    f"Decision ID: {decision_id} | "
                    f"HTTP {response.status_code}"
                )

            else:
                failed += 1

                print(
                    f"[{index:02d}/{len(records)}] "
                    f"FAILED | "
                    f"Shipment ID: {shipment_id} | "
                    f"HTTP {response.status_code}"
                )

                print(
                    f"    {response.text[:500]}"
                )

        except Exception as exc:
            failed += 1

            print(
                f"[{index:02d}/{len(records)}] "
                f"ERROR | "
                f"Shipment ID: {shipment_id} | "
                f"{exc}"
            )

    print()
    print("=" * 60)
    print("BATCH DECISION CREATION COMPLETE")
    print("=" * 60)
    print(f"Total:   {len(records)}")
    print(f"Success: {success}")
    print(f"Failed:  {failed}")


if __name__ == "__main__":
    main()