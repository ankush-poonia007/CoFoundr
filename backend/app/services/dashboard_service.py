# dashboard_service.py
# Purpose: Service layer compiling dashboard analytics summaries.
# Responsibilities:
#   - Query startup, chat, and report repositories for aggregate totals
#   - Build and return serialized dashboard payload dictionaries
# DO NOT: Direct raw SQL query executions without repository classes.
# DO NOT: Run WebSocket broadcast steps directly (delegate to connection manager).

import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.startup_repository import StartupRepository
from app.repositories.chat_repository import ChatRepository
from app.repositories.report_repository import ReportRepository

logger = logging.getLogger(__name__)


class DashboardService:
    """Service class executing metric compilation queries for dashboard interfaces."""

    def __init__(self, db: AsyncSession):
        self.startup_repo = StartupRepository(db)
        self.chat_repo = ChatRepository(db)
        self.report_repo = ReportRepository(db)

    async def get_dashboard_metrics(self, user_id: uuid.UUID) -> dict:
        """
        Compile dashboard metrics, startup averages, recent audits, and chats.

        Args:
            user_id: The UUID of the user.

        Returns:
            dict: Aggregated analytics metrics.
        """
        logger.info(f"Compiling dashboard analytics for user: {user_id}")

        # 1. Fetch startups and averages
        startups = await self.startup_repo.get_by_user_id(user_id)
        total_startups = len(startups)

        avg_health = 0.0
        if total_startups > 0:
            avg_health = sum(s.health_score for s in startups) / total_startups
            avg_health = round(avg_health, 2)

        # 2. Fetch total chat threads
        chats = await self.chat_repo.get_by_user_id(user_id)
        total_chats = len(chats)

        # 3. Fetch reports and compile recent audit list
        total_reports = 0
        recent_reports_list = []
        for startup in startups:
            reports = await self.report_repo.get_by_startup_id(startup.id)
            total_reports += len(reports)
            for r in reports:
                recent_reports_list.append({
                    "id": str(r.id),
                    "startup_name": startup.name,
                    "report_type": r.report_type.value if hasattr(r.report_type, "value") else r.report_type,
                    "score": r.score,
                    "created_at": r.created_at.isoformat() if r.created_at else None
                })

        # Sort recent reports and slice top 5
        recent_reports_list.sort(key=lambda x: x["created_at"] or "", reverse=True)
        recent_reports = recent_reports_list[:5]

        # Compile recent chat threads
        chats_sorted = sorted(chats, key=lambda x: x.updated_at if x.updated_at else x.created_at, reverse=True)
        recent_chats = []
        for c in chats_sorted[:5]:
            recent_chats.append({
                "id": str(c.id),
                "title": c.title,
                "created_at": c.created_at.isoformat() if c.created_at else None
            })

        return {
            "total_startups": total_startups,
            "average_health_score": avg_health,
            "total_chats": total_chats,
            "total_reports": total_reports,
            "recent_reports": recent_reports,
            "recent_chats": recent_chats
        }
