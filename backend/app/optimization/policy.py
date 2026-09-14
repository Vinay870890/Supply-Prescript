from dataclasses import dataclass


@dataclass(frozen=True)
class OptimizationPolicy:
    """
    Business policy controlling the prescriptive optimization engine.

    Changing these values changes the optimizer's business behavior
    without modifying the optimization logic.
    """

    # Objective weights
    cost_weight: float = 0.30
    risk_weight: float = 0.50
    speed_weight: float = 0.20

    # Transportation cost assumptions
    upgrade_cost_multiplier: float = 1.25
    expedite_cost_multiplier: float = 1.60

    # Risk reduction assumptions
    upgrade_risk_multiplier: float = 0.65
    expedite_risk_multiplier: float = 0.35

    # Speed improvement assumptions
    upgrade_speed_bonus: float = 0.20
    expedite_speed_bonus: float = 0.40


DEFAULT_POLICY = OptimizationPolicy()