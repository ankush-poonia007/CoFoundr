# growth_generator_tool.py
# Purpose: Formulate marketing and acquisition growth recommendations.
# Responsibilities:
#   - Expose target channels (e.g. SEO, Cold Outreach, Paid Ads, Virality) matching business model parameters
#   - Estimate acquisition difficulty and focus priorities
# DO NOT: Run LLM model calls directly inside rules.
# DO NOT: Direct database integrations.

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GrowthStrategy:
    """Represents compiled growth strategy recommendations."""
    primary_channels: list[str]
    acquisition_type: str
    focus_advice: str
    timeline_milestone: str


def generate_growth_strategy(startup_data: dict) -> GrowthStrategy:
    """
    Formulate a marketing and customer acquisition strategy.

    Args:
        startup_data: Dictionary of startup metrics.

    Returns:
        GrowthStrategy: Target channels and milestone timeline advice.
    """
    logger.info(f"Generating growth strategy for startup: {startup_data.get('name', 'Unknown')}")

    # Inspect business model details to differentiate B2B from B2C
    biz_model = (startup_data.get("business_model") or "").lower()
    rev_model = (startup_data.get("revenue_model") or "").lower()

    is_b2b = True
    if "b2c" in biz_model or "consumer" in biz_model or "marketplace" in biz_model or "b2c" in rev_model:
        is_b2b = False

    if is_b2b:
        channels = [
            "LinkedIn Cold Outreach (targeted account profiles)",
            "Niche SEO & Content Marketing (thought leadership columns)",
            "Industry Conferences & B2B networking events"
        ]
        acq_type = "B2B Enterprise / SME Sales"
        advice = "Focus on founder-led sales initially. Close your first 5-10 pilot customers manually to build case studies."
        milestone = "Close 5 active paying pilot accounts within 90 days."
    else:
        channels = [
            "Paid Social Media Ads (Meta, TikTok channels)",
            "Influencer & Creator partnerships",
            "In-product referral programs & virality hooks"
        ]
        acq_type = "B2C Consumer Growth"
        advice = "Focus on rapid experimentation and optimizing the onboarding conversion funnel. Track CPA vs LTV closely."
        milestone = "Reach 1,000 active signup users within 60 days."

    return GrowthStrategy(
        primary_channels=channels,
        acquisition_type=acq_type,
        focus_advice=advice,
        timeline_milestone=milestone
    )
