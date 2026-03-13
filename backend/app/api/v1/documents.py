"""Document management API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.pagination import PaginatedResponse, PaginationParams
from app.core.security import get_current_user
from app.schemas.common import SuccessResponse
from app.schemas.document import (
    DocumentClassifyRequest,
    DocumentRead,
    DocumentUpdate,
    DocumentVerifyRequest,
    OCRResultRead,
)
from app.services import document_service

router = APIRouter()


@router.post("/upload", response_model=DocumentRead, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    client_id: UUID = Form(...),
    case_id: UUID | None = Form(default=None),
    document_type: str | None = Form(default=None),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Upload a document file with metadata."""
    return await document_service.upload_document(
        session=session,
        file=file,
        client_id=client_id,
        uploaded_by=current_user.id,
        case_id=case_id,
        document_type=document_type,
    )


@router.get("", response_model=PaginatedResponse[DocumentRead])
async def list_documents(
    pagination: PaginationParams = Depends(),
    client_id: UUID | None = None,
    case_id: UUID | None = None,
    document_type: str | None = None,
    verification_status: str | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """List documents with filters."""
    return await document_service.list_documents(
        session, pagination, client_id, case_id, document_type, verification_status
    )


@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get document metadata by ID."""
    return await document_service.get_document(session, document_id)


@router.put("/{document_id}", response_model=DocumentRead)
async def update_document(
    document_id: UUID,
    payload: DocumentUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Update document metadata."""
    return await document_service.update_document(session, document_id, payload)


@router.delete("/{document_id}", response_model=SuccessResponse)
async def delete_document(
    document_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Soft-delete a document."""
    await document_service.delete_document(session, document_id)
    return SuccessResponse(message="Document deleted successfully")


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Download a document file."""
    data, content_type, filename = await document_service.download_document(session, document_id)
    return Response(
        content=data,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/{document_id}/verify", response_model=DocumentRead)
async def verify_document(
    document_id: UUID,
    payload: DocumentVerifyRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Verify or reject a document."""
    return await document_service.verify_document(
        session, document_id, payload, current_user.id
    )


@router.post("/{document_id}/classify", response_model=DocumentRead)
async def classify_document(
    document_id: UUID,
    payload: DocumentClassifyRequest | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Trigger AI classification of a document."""
    force = payload.force_reclassify if payload else False
    return await document_service.classify_document(session, document_id, force)


@router.get("/{document_id}/ocr", response_model=OCRResultRead)
async def get_ocr_result(
    document_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get OCR results for a document."""
    return await document_service.get_ocr_result(session, document_id)
