import requests

API_BASE = "http://localhost:8001/api"

# CLEAN BATCH CREATED FROM decision_batch_20.json
START_ID = 45
END_ID = 64

success = 0
skipped = 0
failed = 0

print("=" * 60)
print("SUPPLY PRESCRIPT - EXECUTE CLEAN BATCH")
print("=" * 60)

for decision_id in range(START_ID, END_ID + 1):

    try:
        # Check current status
        response = requests.get(
            f"{API_BASE}/decisions/{decision_id}",
            timeout=30
        )

        if response.status_code != 200:
            failed += 1
            print(
                f"[{decision_id}] STATUS CHECK FAILED | "
                f"HTTP {response.status_code}"
            )
            continue

        decision = response.json()
        status = decision.get("decision_status")

        # Already executed
        if status == "EXECUTED":
            skipped += 1
            print(
                f"[{decision_id}] SKIPPED | Already EXECUTED"
            )
            continue

        # Already has outcome
        if status == "OUTCOME_RECORDED":
            skipped += 1
            print(
                f"[{decision_id}] SKIPPED | OUTCOME_RECORDED"
            )
            continue

        # Only SELECTED decisions should be executed
        if status != "SELECTED":
            skipped += 1
            print(
                f"[{decision_id}] SKIPPED | Status: {status}"
            )
            continue

        # Execute decision
        response = requests.post(
            f"{API_BASE}/decisions/{decision_id}/execute",
            json={
                "execution_notes": (
                    "Batch execution for 20 real CSV shipments."
                )
            },
            timeout=30,
        )

        if response.ok:
            success += 1

            print(
                f"[{decision_id}] SUCCESS | "
                f"EXECUTED | HTTP {response.status_code}"
            )

        else:
            failed += 1

            print(
                f"[{decision_id}] FAILED | "
                f"HTTP {response.status_code} | "
                f"{response.text[:300]}"
            )

    except Exception as exc:
        failed += 1

        print(
            f"[{decision_id}] ERROR | {exc}"
        )


print()
print("=" * 60)
print("EXECUTION COMPLETE")
print("=" * 60)
print(f"Batch:    {START_ID}-{END_ID}")
print(f"Total:    {END_ID - START_ID + 1}")
print(f"Executed: {success}")
print(f"Skipped:  {skipped}")
print(f"Failed:   {failed}")