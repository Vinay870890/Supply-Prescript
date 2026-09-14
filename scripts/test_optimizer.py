import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.optimization.optimizer import optimizer
from app.optimization.schemas import OptimizationRequest


request = OptimizationRequest(
    delay_probability=0.0024,
    freight_cost_usd=515.32,
    shipment_value_usd=734.70,
    transport_risk_score=0.2,
    shipment_complexity_score=0.9014,
    shipment_mode="Air",
)

result = optimizer.optimize(request)

print("\nOPTIMIZATION RESULT")
print("===================")

print(f"\nRecommended Action: {result.recommended_action}")
print(f"Reason: {result.recommendation_reason}")

print("\nAlternatives:")

for action in result.alternatives:
    print(
        f"\n{action.action}"
        f"\n  Description: {action.description}"
        f"\n  Cost: ${action.estimated_cost_usd}"
        f"\n  Expected Delay Risk: {action.expected_delay_risk}"
        f"\n  Speed Score: {action.speed_score}"
        f"\n  Risk Score: {action.risk_score}"
        f"\n  Objective Score: {action.objective_score}"
        f"\n  Recommended: {action.recommended}"
    )