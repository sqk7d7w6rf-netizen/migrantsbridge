"""Celery tasks for document processing: OCR and AI classification."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Helper to run async code in a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_ocr(self, document_id: str) -> dict:
    """Process OCR for a document.

    Downloads the document file, extracts text, and stores inline on the Document model.
    """
    logger.info("Starting OCR processing for document %s", document_id)

    async def _process():
        from uuid import UUID

        from sqlalchemy import select

        from app.constants import OcrStatus
        from app.core.database import async_session_factory
        from app.integrations.storage import get_storage_backend
        from app.models.document import Document

        async with async_session_factory() as session:
            result = await session.execute(
                select(Document).where(Document.id == UUID(document_id))
            )
            doc = result.scalar_one_or_none()
            if doc is None:
                logger.error("Document %s not found", document_id)
                return {"status": "error", "message": "Document not found"}

            doc.ocr_status = OcrStatus.PROCESSING
            session.add(doc)
            await session.flush()

            storage = get_storage_backend()
            try:
                file_data = await storage.download(doc.file_path)
            except FileNotFoundError:
                doc.ocr_status = OcrStatus.FAILED
                session.add(doc)
                await session.commit()
                logger.error("File not found in storage for document %s", document_id)
                return {"status": "error", "message": "File not found in storage"}

            # Extract text based on content type
            raw_text = ""
            if doc.mime_type == "application/pdf":
                try:
                    import io
                    try:
                        import pdfplumber
                        with pdfplumber.open(io.BytesIO(file_data)) as pdf:
                            pages_text = []
                            for page in pdf.pages:
                                text = page.extract_text()
                                if text:
                                    pages_text.append(text)
                            raw_text = "\n\n".join(pages_text)
                    except ImportError:
                        raw_text = "[PDF text extraction requires pdfplumber]"
                except Exception as exc:
                    logger.warning("PDF extraction failed for %s: %s", document_id, exc)
                    raw_text = "[PDF extraction failed]"
            elif doc.mime_type and doc.mime_type.startswith("image/"):
                try:
                    import io
                    try:
                        from PIL import Image
                        import pytesseract
                        image = Image.open(io.BytesIO(file_data))
                        raw_text = pytesseract.image_to_string(image)
                    except ImportError:
                        raw_text = "[Image OCR requires pytesseract and Pillow]"
                except Exception as exc:
                    logger.warning("Image OCR failed for %s: %s", document_id, exc)
                    raw_text = "[Image OCR failed]"
            else:
                # Try to decode as text
                try:
                    raw_text = file_data.decode("utf-8", errors="replace")
                except Exception:
                    raw_text = "[Unable to extract text from this file type]"

            # Store OCR result inline on the document
            doc.ocr_text = raw_text
            doc.ocr_status = OcrStatus.COMPLETED if raw_text else OcrStatus.FAILED
            session.add(doc)
            await session.commit()

            logger.info(
                "OCR complete for document %s: %d characters extracted",
                document_id,
                len(raw_text),
            )
            return {"status": "success", "characters": len(raw_text)}

    try:
        return _run_async(_process())
    except Exception as exc:
        logger.exception("OCR task failed for document %s", document_id)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def classify_document(self, document_id: str) -> dict:
    """Use AI to classify a document based on its OCR text."""
    logger.info("Starting AI classification for document %s", document_id)

    async def _classify():
        from uuid import UUID

        from sqlalchemy import select

        from app.constants import DocumentType
        from app.core.database import async_session_factory
        from app.models.document import Document
        from app.services.ai_service import classify_document as ai_classify

        async with async_session_factory() as session:
            # Get document with inline OCR text
            result = await session.execute(
                select(Document).where(Document.id == UUID(document_id))
            )
            doc = result.scalar_one_or_none()

            if doc is None:
                logger.warning("Document %s not found", document_id)
                return {"status": "error", "message": "Document not found"}

            if not doc.ocr_text:
                logger.warning("No OCR text for document %s, skipping classification", document_id)
                return {"status": "skipped", "reason": "No OCR text available"}

            # Classify using AI
            classification = await ai_classify(doc.ocr_text)

            # Update document with classification results
            category = classification.get("category", "other")
            try:
                doc.document_type = DocumentType(category)
            except ValueError:
                doc.document_type = DocumentType.OTHER

            doc.ai_classification = classification.get("extracted_metadata", {})
            doc.ai_confidence = classification.get("confidence", 0.0)
            session.add(doc)
            await session.commit()

            logger.info(
                "Document %s classified as '%s' (confidence: %.2f)",
                document_id,
                category,
                classification.get("confidence", 0.0),
            )
            return {"status": "success", "category": category}

    try:
        return _run_async(_classify())
    except Exception as exc:
        logger.exception("Classification task failed for document %s", document_id)
        raise self.retry(exc=exc)
