"""Document management service with upload handling and OCR triggering."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.constants import DocumentType, OcrStatus
from app.core.pagination import PaginatedResponse, PaginationParams, paginate
from app.integrations.storage import get_storage_backend
from app.models.document import Document
from app.schemas.document import (
    DocumentRead,
    DocumentUpdate,
    DocumentVerifyRequest,
    OCRResultRead,
    VerificationStatus,
)


MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/tiff",
    "image/webp",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


async def _get_document_or_404(session: AsyncSession, document_id: UUID) -> Document:
    result = await session.execute(
        select(Document).where(Document.id == document_id, Document.is_deleted == False)
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc


def _to_document_read(doc: Document) -> DocumentRead:
    """Map the actual model to the schema."""
    v_status = VerificationStatus.VERIFIED if doc.is_verified else VerificationStatus.PENDING
    return DocumentRead(
        id=doc.id,
        client_id=doc.client_id,
        case_id=doc.case_id,
        file_name=doc.file_name,
        original_file_name=doc.file_name,
        content_type=doc.mime_type,
        file_size=doc.file_size,
        document_type=doc.document_type.value if doc.document_type else None,
        storage_path=doc.file_path,
        verification_status=v_status,
        verified_by=doc.verified_by_id,
        verified_at=doc.verified_at,
        expiry_date=datetime.combine(doc.expiration_date, datetime.min.time()) if doc.expiration_date else None,
        notes=doc.ai_summary,
        uploaded_by=doc.uploaded_by_id or doc.client_id,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


async def upload_document(
    session: AsyncSession,
    file: UploadFile,
    client_id: UUID,
    uploaded_by: UUID,
    case_id: UUID | None = None,
    document_type: str | None = None,
) -> DocumentRead:
    """Handle file upload: validate, store, and create metadata record."""
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file.content_type}' is not allowed",
        )

    file_data = await file.read()
    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {MAX_FILE_SIZE // (1024 * 1024)} MB",
        )

    storage = get_storage_backend()
    original_name = file.filename or "unnamed"
    content_type = file.content_type or "application/octet-stream"

    storage_path = await storage.upload(file_data, original_name, content_type)
    checksum = hashlib.sha256(file_data).hexdigest()

    doc_type = None
    if document_type:
        try:
            doc_type = DocumentType(document_type)
        except ValueError:
            doc_type = DocumentType.OTHER

    doc = Document(
        client_id=client_id,
        case_id=case_id,
        title=original_name,
        document_type=doc_type or DocumentType.OTHER,
        file_name=original_name,
        file_path=storage_path,
        file_size=len(file_data),
        mime_type=content_type,
        checksum=checksum,
        storage_backend=settings.STORAGE_BACKEND,
        ocr_status=OcrStatus.PENDING,
        uploaded_by_id=uploaded_by,
    )
    session.add(doc)
    await session.flush()
    await session.refresh(doc)

    # Trigger OCR task asynchronously
    _trigger_ocr(str(doc.id))

    return _to_document_read(doc)


def _trigger_ocr(document_id: str) -> None:
    """Trigger the async OCR processing task."""
    try:
        from app.workers.document_tasks import process_ocr
        process_ocr.delay(document_id)
    except Exception:
        import logging
        logging.getLogger(__name__).warning("Could not queue OCR task for document %s", document_id)


async def get_document(session: AsyncSession, document_id: UUID) -> DocumentRead:
    """Get document metadata by ID."""
    doc = await _get_document_or_404(session, document_id)
    return _to_document_read(doc)


async def list_documents(
    session: AsyncSession,
    pagination: PaginationParams,
    client_id: UUID | None = None,
    case_id: UUID | None = None,
    document_type: str | None = None,
    verification_status: str | None = None,
) -> PaginatedResponse[DocumentRead]:
    """List documents with optional filters."""
    query = select(Document).where(Document.is_deleted == False)

    if client_id:
        query = query.where(Document.client_id == client_id)
    if case_id:
        query = query.where(Document.case_id == case_id)
    if document_type:
        try:
            query = query.where(Document.document_type == DocumentType(document_type))
        except ValueError:
            pass
    if verification_status:
        if verification_status == "verified":
            query = query.where(Document.is_verified == True)
        elif verification_status == "pending":
            query = query.where(Document.is_verified == False)

    query = query.order_by(Document.created_at.desc())
    return await paginate(session, query, pagination, DocumentRead)


async def update_document(
    session: AsyncSession, document_id: UUID, payload: DocumentUpdate
) -> DocumentRead:
    """Update document metadata."""
    doc = await _get_document_or_404(session, document_id)

    update_data = payload.model_dump(exclude_unset=True)
    if "document_type" in update_data and update_data["document_type"] is not None:
        doc.document_type = DocumentType(update_data["document_type"].value)
    if "expiry_date" in update_data:
        doc.expiration_date = update_data["expiry_date"].date() if update_data["expiry_date"] else None
    if "notes" in update_data:
        doc.ai_summary = update_data["notes"]

    session.add(doc)
    await session.flush()
    await session.refresh(doc)
    return _to_document_read(doc)


async def delete_document(session: AsyncSession, document_id: UUID) -> None:
    """Soft-delete a document."""
    doc = await _get_document_or_404(session, document_id)
    doc.is_deleted = True
    doc.deleted_at = datetime.now(timezone.utc)
    session.add(doc)


async def download_document(session: AsyncSession, document_id: UUID) -> tuple[bytes, str, str]:
    """Download a document file. Returns (data, content_type, filename)."""
    doc = await _get_document_or_404(session, document_id)
    storage = get_storage_backend()
    try:
        data = await storage.download(doc.file_path)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found in storage",
        )
    return data, doc.mime_type, doc.file_name


async def verify_document(
    session: AsyncSession,
    document_id: UUID,
    payload: DocumentVerifyRequest,
    verified_by: UUID,
) -> DocumentRead:
    """Verify or reject a document."""
    doc = await _get_document_or_404(session, document_id)

    doc.is_verified = payload.status == VerificationStatus.VERIFIED
    doc.verified_by_id = verified_by
    doc.verified_at = datetime.now(timezone.utc)
    if payload.notes:
        doc.ai_summary = payload.notes

    session.add(doc)
    await session.flush()
    await session.refresh(doc)
    return _to_document_read(doc)


async def classify_document(
    session: AsyncSession, document_id: UUID, force: bool = False
) -> DocumentRead:
    """Trigger AI classification of a document."""
    doc = await _get_document_or_404(session, document_id)

    if doc.ai_classification and not force:
        return _to_document_read(doc)

    try:
        from app.workers.document_tasks import classify_document as classify_task
        classify_task.delay(str(document_id))
    except Exception:
        import logging
        logging.getLogger(__name__).warning(
            "Could not queue classification task for document %s", document_id
        )

    return _to_document_read(doc)


async def get_ocr_result(session: AsyncSession, document_id: UUID) -> OCRResultRead:
    """Get OCR results for a document."""
    doc = await _get_document_or_404(session, document_id)

    if doc.ocr_status != OcrStatus.COMPLETED or not doc.ocr_text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OCR result not available for this document",
        )

    return OCRResultRead(
        id=doc.id,
        document_id=doc.id,
        raw_text=doc.ocr_text,
        extracted_data={"classification": doc.ai_classification} if doc.ai_classification else None,
        confidence_score=doc.ai_confidence,
        language_detected=None,
        processed_at=doc.updated_at,
        created_at=doc.created_at,
    )
