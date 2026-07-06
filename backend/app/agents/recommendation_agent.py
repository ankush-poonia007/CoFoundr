# recommendation_agent.py
# Purpose: Specialized analysis and recommendation agent node.
# Responsibilities:
#   - Parse startup profile metrics from graph state parameters
#   - Call health, risk, MVP, tech, growth, and investor scorer tools
#   - Synthesize scores into a YC-partner style comprehensive advisory audit
# DO NOT: Run raw database select queries inside this agent node.
# DO NOT: Run generic web searches (delegate to web_search_agent.py).

import logging
from app.providers.provider_factory import ProviderFactory
from app.agents.main_agent import AgentState
from app.tools import (
    calculate_health_score,
    analyze_startup_risks,
    generate_mvp_roadmap,
    recommend_tech_stack,
    generate_growth_strategy,
    calculate_investor_readiness
)

logger = logging.getLogger(__name__)


class RecommendationAgent:
    """Agent node that aggregates startup metrics and produces strategic recommendations."""

    async def run(self, state: AgentState) -> AgentState:
        logger.info("RecommendationAgent: Starting strategic startup analysis...")

        # Read startup data from metadata injected by the service layer
        startup_data = state.get("metadata", {}).get("startup_data")

        if not startup_data:
            state["response"] = (
                "No startup profile metrics were found. Please complete the startup onboarding "
                "profile before requesting a recommendation audit."
            )
            return state

        try:
            # 1. Run all heuristic scoring tools
            health = calculate_health_score(startup_data)
            risks = analyze_startup_risks(startup_data)
            mvp = generate_mvp_roadmap(startup_data)
            tech = recommend_tech_stack(startup_data)
            growth = generate_growth_strategy(startup_data)
            investor = calculate_investor_readiness(startup_data)

            # 2. Store scores in state metadata for database caching later
            state["metadata"]["health_score"] = health.total_score
            state["metadata"]["overall_risk"] = risks.overall_rating
            state["metadata"]["investor_score"] = investor.readiness_score

            # 3. Construct the analysis summary prompt
            concerns_text = "\n".join([f"- {c}" for c in risks.concerns]) if risks.concerns else "- None detected."
            gaps_text = "\n".join([f"- {g}" for g in investor.gap_analysis]) if investor.gap_analysis else "- None detected."
            phases_text = "\n".join([f"- {p['phase']} ({p['duration']}): {p['goal']}" for p in mvp.phases])

            analysis_context = (
                f"Startup Profile: {startup_data.get('name')}\n"
                f"Tagline: {startup_data.get('tagline')}\n"
                f"Stage: {startup_data.get('stage')}\n\n"
                f"--- SCORES & METRICS ---\n"
                f"- Health Score: {health.total_score}/100 ({health.grade}) - {health.summary}\n"
                f"- Risk Rating: {risks.overall_rating} (Market: {risks.market_risk}, Exec: {risks.execution_risk}, Fin: {risks.financial_risk}, Tech: {risks.tech_risk})\n"
                f"- Tech Moat: language={tech.language}, databases={tech.database}, backend={tech.backend}\n"
                f"- Growth Mode: {growth.acquisition_type} targeting channels: {', '.join(growth.primary_channels)}\n"
                f"- Investor Readiness: {investor.readiness_score}/100 (Recommended bucket: {investor.funding_stage_recommended})\n\n"
                f"--- CONCERNS IDENTIFIED ---\n"
                f"{concerns_text}\n\n"
                f"--- INVESTOR GAPS CHECKLIST ---\n"
                f"{gaps_text}\n\n"
                f"--- MVP ROADMAP TIMELINE: {mvp.target_timeline} ---\n"
                f"{phases_text}"
            )

            synthesis_prompt = (
                f"You are a Y Combinator Managing Partner. Synthesize the startup scoring data below into a comprehensive advisory report:\n\n"
                f"{analysis_context}\n\n"
                "Format your report in markdown with the following sections:\n"
                "## Executive Summary (YC Partner assessment)\n"
                "## Core Moats & Defensibility (Competitive advantage analysis)\n"
                "## Architecture & Infrastructure Moat (Tech recommendations review)\n"
                "## Strategic Growth Flywheel (Customer acquisition advice)\n"
                "## Funding & Investor Gaps (How to bridge seed requirements)\n"
                "## Actionable Milestones (A step-by-step immediate task list)\n\n"
                "Provide critical, direct, and actionable advice. Do not hold back on weaknesses, but outline a path to clear them."
            )

            provider = ProviderFactory.get_reasoning_provider()
            response = await provider.generate(
                prompt=synthesis_prompt,
                system_prompt="You are a veteran YC managing partner and startup builder. Your advice is legendary, direct, and highly strategic."
            )

            state["response"] = response.content

        except Exception as e:
            logger.error(f"RecommendationAgent: Analytics synthesis failed: {e}")
            state["response"] = "I encountered an error executing the startup advisory calculations."

        return state
