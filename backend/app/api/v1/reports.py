# reports.py
# Purpose: Startup analysis reports API endpoint router.
# Responsibilities:
#   - Route reports retrieval listings and detail queries to ReportService
#   - Expose PDF file download endpoints streaming binary data payloads
# DO NOT: Run PDF compilation or rendering tasks inside endpoint methods directly.
# DO NOT: Bypass user authentication checks.

import logging
import uuid
from typing import List
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user_id
from app.schemas.report import ReportResponse
from app.services.report_service import ReportService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports")


@router.get("", response_model=List[ReportResponse])
async def list_reports(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all reports generated for the user's startups."""
    logger.info(f"REST request: Listing reports for user {user_id}")
    return await ReportService(db).list_reports(user_id)


@router.get("/{id}", response_model=ReportResponse)
async def get_report(
    id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve details of a specific report."""
    logger.info(f"REST request: Fetching report {id} for user {user_id}")
    return await ReportService(db).get_report(id, user_id)


@router.get("/{id}/download")
async def download_report_pdf(
    id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Compile and stream the report PDF file directly to the client browser."""
    logger.info(f"REST request: Downloading PDF for report {id} for user {user_id}")
    pdf_bytes = await ReportService(db).get_report_pdf(id, user_id)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=cofoundr_report_{id}.pdf"
        }
    )
