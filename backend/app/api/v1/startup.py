# startup.py
# Purpose: Startup profile management API endpoint router.
# Responsibilities:
#   - Route startup profile updates and creation requests to StartupService
#   - Route strategic recommendations assessment commands to StartupService
# DO NOT: Write raw validation logic or execute DB queries directly.
# DO NOT: Parse raw JSON configurations without Pydantic verification.

import logging
import uuid
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.tools import parse_file, index_document

from app.db.session import get_db
from app.api.deps import get_current_user_id
from app.schemas.startup import StartupCreate, StartupUpdate, StartupResponse
from app.services.startup_service import StartupService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/startups")


@router.get("", response_model=List[StartupResponse])
async def list_startups(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all startup profiles registered by the authenticated user."""
    logger.info(f"Listing startups for user: {user_id}")
    return await StartupService(db).list_startups(user_id)


@router.post("", response_model=StartupResponse, status_code=status.HTTP_201_CREATED)
async def create_startup(
    payload: StartupCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Register a new startup profile."""
    logger.info(f"Registering startup profile for user: {user_id}")
    return await StartupService(db).create_startup(user_id, payload)


@router.get("/{id}", response_model=StartupResponse)
async def get_startup(
    id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve details of a specific startup profile."""
    logger.info(f"Fetching startup: {id} for user: {user_id}")
    return await StartupService(db).get_startup(id, user_id)


@router.put("/{id}", response_model=StartupResponse)
async def update_startup(
    id: uuid.UUID,
    payload: StartupUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Modify parameters of an existing startup profile."""
    logger.info(f"Updating startup profile: {id} for user: {user_id}")
    return await StartupService(db).update_startup(id, user_id, payload)


@router.post("/{id}/analyze")
async def analyze_startup(
    id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Run the YC partner recommendations workflow, computing metrics and compiling audits."""
    logger.info(f"Triggering strategic analysis for startup: {id} for user: {user_id}")
    return await StartupService(db).analyze_startup(id, user_id)


@router.post("/{id}/documents")
async def upload_document(
    id: uuid.UUID,
    file: UploadFile = File(...),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Upload and vector-index a document for a specific startup profile."""
    logger.info(f"Uploading file {file.filename} for startup: {id}")
    # 1. Verify startup ownership
    startup_service = StartupService(db)
    startup = await startup_service.startup_repo.get(id)
    if not startup or startup.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup profile not found."
        )

    # 2. Read and parse file
    file_content = await file.read()
    try:
        parsed_text = parse_file(file_content, file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse uploaded document: {str(e)}"
        )

    # 3. Vector-index chunks
    chunks_count = await index_document(id, file.filename, parsed_text)

    return {
        "filename": file.filename,
        "chunks_indexed": chunks_count,
        "message": "File indexed successfully."
    }

