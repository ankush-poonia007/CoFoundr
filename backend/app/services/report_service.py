# report_service.py
# Purpose: Service layer orchestrating report queries and PDF stream compilation.
# Responsibilities:
#   - List and fetch generated reports verifying user ownership
#   - Trigger ReportLab PDF compiler to output raw PDF bytes
# DO NOT: Write files to the server filesystem under production runs.
# DO NOT: Parse HTTP request structures directly.

import logging
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.repositories.report_repository import ReportRepository
from app.repositories.startup_repository import StartupRepository
from app.utils.pdf_generator import generate_report_pdf
from app.schemas.report import ReportResponse

logger = logging.getLogger(__name__)


class ReportService:
    """Service class executing business transactions for generated reports."""

    def __init__(self, db: AsyncSession):
        self.report_repo = ReportRepository(db)
        self.startup_repo = StartupRepository(db)

    async def list_reports(self, user_id: uuid.UUID) -> List[ReportResponse]:
        """Fetch all reports generated for all startups owned by this user."""
        logger.info(f"Listing all reports for user: {user_id}")
        startups = await self.startup_repo.get_by_user_id(user_id)
        if not startups:
            return []

        all_reports = []
        for startup in startups:
            reports = await self.report_repo.get_by_startup_id(startup.id)
            all_reports.extend([ReportResponse.model_validate(r) for r in reports])

        return all_reports

    async def get_report(self, report_id: uuid.UUID, user_id: uuid.UUID) -> ReportResponse:
        """Fetch a specific report profile, validating user ownership."""
        logger.info(f"Fetching report details: {report_id}")
        report = await self.report_repo.get(report_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report record not found."
            )

        # Validate startup ownership
        startup = await self.startup_repo.get(report.startup_id)
        if not startup or startup.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to report resource."
            )

        return ReportResponse.model_validate(report)

    async def get_report_pdf(self, report_id: uuid.UUID, user_id: uuid.UUID) -> bytes:
        """
        Fetch report markdown, compile it to PDF bytes using ReportLab,
        and return the raw byte stream.
        """
        logger.info(f"Compiling PDF bytes for report: {report_id}")
        report = await self.report_repo.get(report_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report record not found."
            )

        # Validate startup ownership
        startup = await self.startup_repo.get(report.startup_id)
        if not startup or startup.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to report resource."
            )

        # Generate PDF document title
        report_title = f"{startup.name} - {str(report.report_type.value).replace('_', ' ').title()}"

        try:
            pdf_bytes = generate_report_pdf(report_title, report.content)
            return pdf_bytes
        except Exception as e:
            logger.error(f"ReportService: PDF compilation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate PDF document."
            )
