# __init__.py
# Purpose: Initialize the tools package.
# Responsibilities:
#   - Expose the Tavily search client, file parser, and ChromaDB hybrid search tools
# DO NOT: Put search, vector DB logic, or parser functions directly inside this file.

from app.tools.web_search_tool import (
    search_web,
    search_competitors,
    search_market_size,
    search_funding,
    search_tech_stack,
)
from app.tools.file_parser_tool import parse_file
from app.tools.embedder_tool import embed_text, embed_texts
from app.tools.hybrid_search_tool import index_document, search_documents
from app.tools.health_scorer_tool import calculate_health_score
from app.tools.risk_analyzer_tool import analyze_startup_risks
from app.tools.mvp_generator_tool import generate_mvp_roadmap
from app.tools.tech_recommender_tool import recommend_tech_stack
from app.tools.growth_generator_tool import generate_growth_strategy
from app.tools.investor_scorer_tool import calculate_investor_readiness

