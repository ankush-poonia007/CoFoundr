# test_dashboard.py
# Purpose: Unit tests for dashboard service calculations.
# Responsibilities:
#   - Mock repositories and verify dashboard compiling aggregates correctly
# DO NOT: Connect to live databases.

from unittest.mock import AsyncMock
import pytest
import uuid
from app.services.dashboard_service import DashboardService


@pytest.mark.asyncio
async def test_dashboard_compiles_correctly():
    """Verify get_dashboard_metrics retrieves totals and averages properly."""
    # 1. Setup Mock DB session
    mock_db = AsyncMock()
    service = DashboardService(db=mock_db)

    # Override standard repositories with AsyncMocks
    service.startup_repo = AsyncMock()
    service.chat_repo = AsyncMock()
    service.report_repo = AsyncMock()

    user_id = uuid.uuid4()

    # Configure mock startups list
    mock_startup_1 = AsyncMock()
    mock_startup_1.id = uuid.uuid4()
    mock_startup_1.name = "Startup 1"
    mock_startup_1.health_score = 80.0

    mock_startup_2 = AsyncMock()
    mock_startup_2.id = uuid.uuid4()
    mock_startup_2.name = "Startup 2"
    mock_startup_2.health_score = 60.0

    service.startup_repo.get_by_user_id.return_value = [mock_startup_1, mock_startup_2]

    # Configure mock chats
    mock_chat = AsyncMock()
    mock_chat.id = uuid.uuid4()
    mock_chat.title = "Chat thread 1"
    mock_chat.created_at = None
    mock_chat.updated_at = None
    service.chat_repo.get_by_user_id.return_value = [mock_chat]

    # Configure mock reports
    mock_report = AsyncMock()
    mock_report.id = uuid.uuid4()
    mock_report.report_type.value = "investor_readiness"
    mock_report.score = 70.0
    mock_report.created_at = None
    service.report_repo.get_by_startup_id.return_value = [mock_report]

    # 2. Trigger analytics compiler
    metrics = await service.get_dashboard_metrics(user_id)

    # 3. Assert correct aggregates are loaded
    assert metrics["total_startups"] == 2
    assert metrics["average_health_score"] == 70.0  # (80 + 60) / 2
    assert metrics["total_chats"] == 1
    assert metrics["total_reports"] == 2            # 1 report per startup
    assert len(metrics["recent_reports"]) == 2
    assert len(metrics["recent_chats"]) == 1
