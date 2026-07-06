# startup_service.py
# Purpose: Service layer orchestrating startup profile and strategic recommendations actions.
# Responsibilities:
#   - Manage startup profile CRUD operations using StartupRepository
#   - Formulate recommendation state triggers and index evaluations to database
# DO NOT: Parse raw request bodies or return HTTP responses directly.
# DO NOT: Query database transaction logs without repository classes.

import logging
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.agents.graph import agent_graph
from app.models.enums import ReportType
from app.repositories.startup_repository import StartupRepository
from app.repositories.report_repository import ReportRepository
from app.schemas.startup import StartupCreate, StartupUpdate, StartupResponse

logger = logging.getLogger(__name__)


class StartupService:
    """Service class executing business transactions for startup endpoints."""

    def __init__(self, db: AsyncSession):
        self.startup_repo = StartupRepository(db)
        self.report_repo = ReportRepository(db)
        self.db = db

    async def list_startups(self, user_id: uuid.UUID) -> List[StartupResponse]:
        """Retrieve all startup profiles registered by the user."""
        startups = await self.startup_repo.get_by_user_id(user_id)
        return [StartupResponse.model_validate(s) for s in startups]

    async def get_startup(self, startup_id: uuid.UUID, user_id: uuid.UUID) -> StartupResponse:
        """Fetch details of a specific startup profile, checking owner credentials."""
        startup = await self.startup_repo.get(startup_id)
        if not startup or startup.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Startup profile not found."
            )
        return StartupResponse.model_validate(startup)

    async def create_startup(self, user_id: uuid.UUID, payload: StartupCreate) -> StartupResponse:
        """Register a new startup profile for the user."""
        startup = await self.startup_repo.create({
            **payload.model_dump(),
            "user_id": user_id,
            "health_score": 0.0
        })
        await self.db.commit()
        return StartupResponse.model_validate(startup)

    async def update_startup(
        self,
        startup_id: uuid.UUID,
        user_id: uuid.UUID,
        payload: StartupUpdate
    ) -> StartupResponse:
        """Modify parameters of an existing startup profile, checking owner credentials."""
        startup = await self.startup_repo.get(startup_id)
        if not startup or startup.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Startup profile not found."
            )

        updated = await self.startup_repo.update(
            startup,
            payload.model_dump(exclude_unset=True)
        )
        await self.db.commit()
        return StartupResponse.model_validate(updated)

    async def analyze_startup(self, startup_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        """
        Run the YC partner strategic recommendation workflow.
        Calculates score indices, stores generated audit text, and caches score in Postgres.
        """
        startup = await self.startup_repo.get(startup_id)
        if not startup or startup.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Startup profile not found."
            )

        # Structure metrics as serializable dictionary parameters
        startup_data = {
            "name": startup.name,
            "tagline": startup.tagline,
            "problem_statement": startup.problem_statement,
            "solution_description": startup.solution_description,
            "target_market": startup.target_market,
            "unique_value_proposition": startup.unique_value_proposition,
            "founder_name": startup.founder_name,
            "team_size": startup.team_size,
            "domain_expertise": startup.domain_expertise,
            "stage": startup.stage.value if hasattr(startup.stage, "value") else startup.stage,
            "business_model": startup.business_model,
            "revenue_model": startup.revenue_model,
            "has_revenue": startup.has_revenue,
            "competitors_known": startup.competitors_known,
            "competitive_advantage": startup.competitive_advantage,
        }

        # Configure initial state, forcing classification routing to recommendations agent
        initial_state = {
            "messages": [{"role": "user", "content": "Execute YC recommendations report and metric scoring."}],
            "startup_id": str(startup_id),
            "next_agent": None,
            "response": None,
            "metadata": {
                "startup_data": startup_data
            }
        }

        try:
            # Trigger LangGraph workflows
            result = await agent_graph.ainvoke(initial_state)

            report_content = result.get("response") or "Analysis completed with empty advisory output."
            health_score = result.get("metadata", {}).get("health_score", 0.0)

            # Update startup profile cached score
            await self.startup_repo.update(startup, {"health_score": health_score})

            # Append generated analysis report to history logs
            report_obj = await self.report_repo.create({
                "startup_id": startup_id,
                "report_type": ReportType.INVESTOR_READINESS,
                "content": report_content,
                "score": health_score,
                "metadata_json": result.get("metadata")
            })

            await self.db.commit()

            return {
                "report_id": report_obj.id,
                "health_score": health_score,
                "report": report_content
            }

        except Exception as e:
            logger.error(f"StartupService: Analysis workflow failed: {e}")
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to compute startup advisor analysis."
            )
