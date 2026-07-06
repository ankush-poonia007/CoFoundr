# investor_scorer_tool.py
# Purpose: Formulate fundraising and investor readiness evaluations.
# Responsibilities:
#   - Compute a readiness index based on stage, revenue, and competitive barriers
#   - Expose actionable steps to bridge funding gaps
# DO NOT: Run LLM model calls directly inside rules.
# DO NOT: Direct database integrations.

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class InvestorReadinessProfile:
    """Represents compiled investor readiness results."""
    readiness_score: float
    funding_stage_recommended: str
    readiness_factors: list[dict]
    gap_analysis: list[str]


def calculate_investor_readiness(startup_data: dict) -> InvestorReadinessProfile:
    """
    Calculate an investor readiness index based on product stage, metrics, and team strength.

    Args:
        startup_data: Dictionary of startup metrics.

    Returns:
        InvestorReadinessProfile: Computed score, funding bucket, and gap checklists.
    """
    logger.info(f"Calculating investor readiness for startup: {startup_data.get('name', 'Unknown')}")

    score = 30.0  # Baseline index

    # 1. Product Stage weights
    stage = startup_data.get("stage", "idea")
    if hasattr(stage, "value"):
        stage = stage.value

    stage_points = {
        "idea": 5.0,
        "validation": 10.0,
        "prototype": 15.0,
        "mvp": 20.0,
        "early": 25.0,
        "growing": 30.0,
        "scaling": 35.0
    }
    score += stage_points.get(str(stage), 5.0)

    # 2. Traction / Revenue weights
    if startup_data.get("has_revenue"):
        score += 20.0
    elif startup_data.get("business_model") or startup_data.get("revenue_model"):
        score += 10.0

    # 3. Team composition weights
    if startup_data.get("domain_expertise"):
        score += 15.0
    team_size = startup_data.get("team_size", 1)
    if team_size > 1:
        score += 10.0

    # 4. Competitive defensibility weight
    if startup_data.get("competitive_advantage"):
        score += 10.0

    score = min(score, 100.0)

    # Match funding stage recommendation based on computed score
    if score >= 75:
        funding_stage = "Seed / Institutional Pre-Seed"
    elif score >= 50:
        funding_stage = "Angel Pre-Seed / Incubators"
    else:
        funding_stage = "Bootstrap / Friends & Family"

    # Compile fundraising barriers / gaps checklist
    gaps = []
    if str(stage) in ["idea", "validation"]:
        gaps.append("Lacks functional prototype: VCs rarely fund conceptual ideas without a demo.")
    if not startup_data.get("has_revenue"):
        gaps.append("Zero market traction: lack of active revenue or proof-of-concept user metrics.")
    if team_size == 1:
        gaps.append("Solo founder: institutional investors prefer co-founding team configurations.")
    if not startup_data.get("competitive_advantage"):
        gaps.append("Undocumented moat: missing clear long-term competitive advantage to defend market share.")

    factors = [
        {"factor": "Product Maturity", "status": "Strong" if score > 70 else "Medium" if score > 45 else "Weak"},
        {"factor": "Team Configuration", "status": "Strong" if team_size > 1 and startup_data.get("domain_expertise") else "Weak"},
        {"factor": "Financial Traction", "status": "Strong" if startup_data.get("has_revenue") else "Weak"}
    ]

    return InvestorReadinessProfile(
        readiness_score=score,
        funding_stage_recommended=funding_stage,
        readiness_factors=factors,
        gap_analysis=gaps
    )
