# test_recommendations.py
# Purpose: Unit tests for startup assessment heuristic calculation tools.
# Responsibilities:
#   - Validate health scorer weights, grades, and bounds
#   - Validate risk assessment categories and compiled concerns lists
#   - Validate MVP roadmap timeline divisions and features
#   - Validate tech recommendation verticals, growth acquisition types, and investor score ratios
# DO NOT: Connect to external PostgreSQL databases.
# DO NOT: Execute live LLM API calls in calculations testing.

import pytest
from app.models.enums import StartupStage
from app.tools import (
    calculate_health_score,
    analyze_startup_risks,
    generate_mvp_roadmap,
    recommend_tech_stack,
    generate_growth_strategy,
    calculate_investor_readiness
)


@pytest.fixture
def mock_startup_data():
    """Fixture returning sample structured startup profile metadata."""
    return {
        "name": "Acme AI",
        "tagline": "The future of automation",
        "problem_statement": "Businesses waste time on manual scheduling tasks.",
        "solution_description": "Auto scheduler via API and agents.",
        "target_market": "B2B SaaS companies",
        "unique_value_proposition": "10x faster scheduling using agentic routing.",
        "founder_name": "John Doe",
        "team_size": 2,
        "domain_expertise": "5 years in scheduling systems development",
        "stage": StartupStage.MVP,
        "business_model": "SaaS B2B",
        "revenue_model": "Per user seat licensing fee",
        "has_revenue": True,
        "competitors_known": True,
        "competitive_advantage": "Proprietary scheduling heuristic algorithm"
    }


def test_health_scorer_math(mock_startup_data):
    """Verify health score calculations return correct range, breakdown, and grades."""
    res = calculate_health_score(mock_startup_data)
    assert 0 <= res.total_score <= 100
    assert res.grade in ["A", "B", "C", "D", "F"]
    assert isinstance(res.summary, str)


def test_risk_analyzer_breakdown(mock_startup_data):
    """Verify risk analyzer returns ratings and compiler concerns lists."""
    res = analyze_startup_risks(mock_startup_data)
    assert res.overall_rating in ["Low", "Medium", "High"]
    assert res.market_risk in ["Low", "Medium", "High"]
    assert isinstance(res.concerns, list)


def test_mvp_generator_roadmap(mock_startup_data):
    """Verify MVP generator roadmap timeline ranges and backlog features."""
    res = generate_mvp_roadmap(mock_startup_data)
    assert "Weeks" in res.target_timeline
    assert len(res.phases) > 0
    assert len(res.key_features) > 0


def test_tech_recommender(mock_startup_data):
    """Verify tech stack recommendations match domains and vertical rules."""
    res = recommend_tech_stack(mock_startup_data)
    assert "FastAPI" in res.backend
    assert "PostgreSQL" in res.database
    assert len(res.rationale) > 0


def test_growth_strategy_generator(mock_startup_data):
    """Verify growth strategy returns acquisition categories and timeline milestone targets."""
    res = generate_growth_strategy(mock_startup_data)
    assert len(res.primary_channels) > 0
    assert "B2B" in res.acquisition_type
    assert len(res.focus_advice) > 0


def test_investor_readiness_scorer(mock_startup_data):
    """Verify investor readiness scores, recommended funding stages, and gap checklists."""
    res = calculate_investor_readiness(mock_startup_data)
    assert 0 <= res.readiness_score <= 100
    assert isinstance(res.funding_stage_recommended, str)
    assert isinstance(res.gap_analysis, list)
