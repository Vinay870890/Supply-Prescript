from app.optimization.policy import (
    DEFAULT_POLICY,
    OptimizationPolicy,
)
from app.optimization.schemas import (
    ActionRecommendation,
    OptimizationRequest,
    OptimizationResponse,
)


class ShipmentOptimizer:
    """
    Explainable rule-based prescriptive optimization engine.

    Objective:
        minimize
            cost penalty + risk penalty + speed penalty

    The optimizer evaluates three business actions:

        1. KEEP_CURRENT
        2. UPGRADE_TRANSPORT
        3. EXPEDITE

    Business assumptions are controlled through OptimizationPolicy.
    """

    def __init__(
        self,
        policy: OptimizationPolicy = DEFAULT_POLICY,
    ):
        self.policy = policy

    def optimize(
        self,
        request: OptimizationRequest,
    ) -> OptimizationResponse:

        delay_probability = request.delay_probability
        freight_cost = request.freight_cost_usd
        shipment_value = request.shipment_value_usd
        transport_risk = request.transport_risk_score
        complexity = request.shipment_complexity_score

        actions: list[ActionRecommendation] = []

        # =========================================================
        # ACTION 1 — KEEP CURRENT
        # =========================================================

        current_risk = min(
            1.0,
            delay_probability
            + (transport_risk * 0.10)
            + (complexity * 0.05),
        )

        current_cost = freight_cost

        current_speed = max(
            0.0,
            1.0 - delay_probability,
        )

        current_score = self._objective(
            cost=current_cost,
            shipment_value=shipment_value,
            risk=current_risk,
            speed=current_speed,
        )

        actions.append(
            ActionRecommendation(
                action="KEEP_CURRENT",
                description=(
                    "Continue with the existing transportation plan."
                ),
                estimated_cost_usd=round(
                    current_cost,
                    2,
                ),
                expected_delay_risk=round(
                    current_risk,
                    4,
                ),
                speed_score=round(
                    current_speed,
                    4,
                ),
                risk_score=round(
                    1.0 - current_risk,
                    4,
                ),
                objective_score=round(
                    current_score,
                    4,
                ),
            )
        )

        # =========================================================
        # ACTION 2 — UPGRADE TRANSPORT
        # =========================================================

        upgrade_cost = (
            freight_cost
            * self.policy.upgrade_cost_multiplier
        )

        upgrade_risk = max(
            0.0,
            delay_probability
            * self.policy.upgrade_risk_multiplier
            + (transport_risk * 0.05),
        )

        upgrade_speed = min(
            1.0,
            current_speed
            + self.policy.upgrade_speed_bonus,
        )

        upgrade_score = self._objective(
            cost=upgrade_cost,
            shipment_value=shipment_value,
            risk=upgrade_risk,
            speed=upgrade_speed,
        )

        actions.append(
            ActionRecommendation(
                action="UPGRADE_TRANSPORT",
                description=(
                    "Move the shipment to a faster or "
                    "lower-risk transportation option."
                ),
                estimated_cost_usd=round(
                    upgrade_cost,
                    2,
                ),
                expected_delay_risk=round(
                    upgrade_risk,
                    4,
                ),
                speed_score=round(
                    upgrade_speed,
                    4,
                ),
                risk_score=round(
                    1.0 - upgrade_risk,
                    4,
                ),
                objective_score=round(
                    upgrade_score,
                    4,
                ),
            )
        )

        # =========================================================
        # ACTION 3 — EXPEDITE
        # =========================================================

        expedite_cost = (
            freight_cost
            * self.policy.expedite_cost_multiplier
        )

        expedite_risk = max(
            0.0,
            delay_probability
            * self.policy.expedite_risk_multiplier,
        )

        expedite_speed = min(
            1.0,
            current_speed
            + self.policy.expedite_speed_bonus,
        )

        expedite_score = self._objective(
            cost=expedite_cost,
            shipment_value=shipment_value,
            risk=expedite_risk,
            speed=expedite_speed,
        )

        actions.append(
            ActionRecommendation(
                action="EXPEDITE",
                description=(
                    "Use an expedited transportation option "
                    "to minimize delay risk."
                ),
                estimated_cost_usd=round(
                    expedite_cost,
                    2,
                ),
                expected_delay_risk=round(
                    expedite_risk,
                    4,
                ),
                speed_score=round(
                    expedite_speed,
                    4,
                ),
                risk_score=round(
                    1.0 - expedite_risk,
                    4,
                ),
                objective_score=round(
                    expedite_score,
                    4,
                ),
            )
        )

        # =========================================================
        # SELECT BEST ACTION
        # =========================================================

        actions.sort(
            key=lambda action: action.objective_score
        )

        # Mark the lowest-objective action as recommended.
        actions[0].recommended = True

        recommended = actions[0]

        # =========================================================
        # BUILD EXPLANATION
        # =========================================================

        reason = self._build_reason(
            recommendation=recommended,
            delay_probability=delay_probability,
        )

        return OptimizationResponse(
            success=True,
            recommended_action=recommended.action,
            recommendation_reason=reason,
            alternatives=actions,
        )

    # =============================================================
    # OBJECTIVE FUNCTION
    # =============================================================

    def _objective(
        self,
        cost: float,
        shipment_value: float,
        risk: float,
        speed: float,
    ) -> float:
        """
        Calculate the business objective score.

        Lower score = better recommendation.

        Components:

            Cost penalty
            Risk penalty
            Speed penalty

        All components are normalized to approximately [0, 1].
        """

        # ---------------------------------------------------------
        # Normalize transportation cost against shipment value.
        # ---------------------------------------------------------

        normalized_cost = min(
            1.0,
            cost / max(
                shipment_value,
                1.0,
            ),
        )

        # ---------------------------------------------------------
        # Speed penalty.
        #
        # speed = 1.0  -> no penalty
        # speed = 0.0  -> maximum penalty
        # ---------------------------------------------------------

        speed_penalty = 1.0 - speed

        # ---------------------------------------------------------
        # Business weights from policy.
        # ---------------------------------------------------------

        cost_weight = self.policy.cost_weight
        risk_weight = self.policy.risk_weight
        speed_weight = self.policy.speed_weight

        # ---------------------------------------------------------
        # Final objective.
        # ---------------------------------------------------------

        score = (
            cost_weight * normalized_cost
            + risk_weight * risk
            + speed_weight * speed_penalty
        )

        return score

    # =============================================================
    # EXPLANATION
    # =============================================================

    def _build_reason(
        self,
        recommendation: ActionRecommendation,
        delay_probability: float,
    ) -> str:
        """
        Generate a human-readable explanation for the
        recommended business action.
        """

        probability_percent = round(
            delay_probability * 100,
            1,
        )

        # ---------------------------------------------------------
        # KEEP CURRENT
        # ---------------------------------------------------------

        if recommendation.action == "KEEP_CURRENT":
            return (
                f"Current predicted delay probability is "
                f"{probability_percent}%, so maintaining the "
                f"existing transportation plan provides the best "
                f"cost-risk-speed trade-off."
            )

        # ---------------------------------------------------------
        # UPGRADE TRANSPORT
        # ---------------------------------------------------------

        if recommendation.action == "UPGRADE_TRANSPORT":
            return (
                f"The predicted delay probability is "
                f"{probability_percent}%. Upgrading transportation "
                f"provides a better risk reduction without the full "
                f"cost of expedited shipping."
            )

        # ---------------------------------------------------------
        # EXPEDITE
        # ---------------------------------------------------------

        return (
            f"The predicted delay probability is "
            f"{probability_percent}%. Expediting provides the "
            f"largest reduction in expected delay risk."
        )


# ================================================================
# DEFAULT OPTIMIZER INSTANCE
# ================================================================

optimizer = ShipmentOptimizer(
    policy=DEFAULT_POLICY,
)