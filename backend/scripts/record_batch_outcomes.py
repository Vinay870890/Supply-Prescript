import json
from pathlib import Path

import requests


BASE_DIR = Path(__file__).resolve().parents[2]

OUTCOME_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "decision_batch_20_outcomes.json"
)

API_URL = "http://localhost:8001/api/outcomes"

START_DECISION_ID = 45
END_DECISION_ID = 64


def main():
    if not OUTCOME_FILE.exists():
        raise FileNotFoundError(
            f"Outcome file not found: {OUTCOME_FILE}"
        )

    with open(OUTCOME_FILE, "r", encoding="utf-8") as f:
        outcomes = json.load(f)

    print("=" * 60)
    print("SUPPLY PRESCRIPT - RECORD BATCH OUTCOMES")
    print("=" * 60)
    print(f"Loaded {len(outcomes)} historical outcomes.")
    print(f"Decision range: {START_DECISION_ID}-{END_DECISION_ID}")
    print()

    success = 0
    skipped = 0
    failed = 0

    # Match outcomes to the clean decision batch by position.
    if len(outcomes) != 20:
        raise ValueError(
            f"Expected 20 outcomes, found {len(outcomes)}."
        )

    for index, outcome in enumerate(outcomes):
        decision_id = START_DECISION_ID + index

        shipment_id = outcome.get("shipment_id")

        payload = {
            "decision_id": decision_id,
            "shipment_id": shipment_id,
            "actual_delay_days": outcome["actual_delay_days"],
            "actual_delay_flag": outcome["actual_delay_flag"],
            "actual_cost_usd": outcome["actual_cost_usd"],
            "outcome_status": outcome["outcome_status"],
            "outcome_notes": outcome.get("outcome_notes"),
        }

        try:
            response = requests.post(
                API_URL,
                json=payload,
                timeout=30,
            )

            if response.ok:
                success += 1

                result = response.json()

                print(
                    f"[{index + 1:02d}/20] SUCCESS | "
                    f"Decision ID: {decision_id} | "
                    f"Shipment ID: {shipment_id} | "
                    f"Outcome ID: {result.get('id', 'N/A')}"
                )

            elif response.status_code == 400 and (
                "already recorded" in response.text.lower()
            ):
                skipped += 1

                print(
                    f"[{index + 1:02d}/20] SKIPPED | "
                    f"Decision ID: {decision_id} | "
                    f"Outcome already recorded"
                )

            else:
                failed += 1

                print(
                    f"[{index + 1:02d}/20] FAILED | "
                    f"Decision ID: {decision_id} | "
                    f"HTTP {response.status_code}"
                )

                print(
                    f"    {response.text[:500]}"
                )

        except Exception as exc:
            failed += 1

            print(
                f"[{index + 1:02d}/20] ERROR | "
                f"Decision ID: {decision_id} | "
                f"{exc}"
            )

    print()
    print("=" * 60)
    print("OUTCOME RECORDING COMPLETE")
    print("=" * 60)
    print(f"Total:   20")
    print(f"Success: {success}")
    print(f"Skipped: {skipped}")
    print(f"Failed:  {failed}")


if __name__ == "__main__":
    main()