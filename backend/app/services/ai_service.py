"""AI service: Claude API integration for workflow generation, document classification, eligibility assessment, and routing."""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import ValidationError

from app.integrations.claude import claude_client
from app.prompts.document_classification import (
    DOCUMENT_CLASSIFICATION_SYSTEM,
    DOCUMENT_CLASSIFICATION_USER,
)
from app.prompts.eligibility import ELIGIBILITY_SYSTEM, ELIGIBILITY_USER
from app.prompts.task_routing import TASK_ROUTING_SYSTEM, TASK_ROUTING_USER
from app.prompts.workflow_generation import (
    WORKFLOW_GENERATION_SYSTEM,
    WORKFLOW_GENERATION_USER,
)
from app.schemas.ai import (
    DocumentClassificationAI,
    EligibilityAssessmentAI,
    TaskRoutingAI,
    WorkflowAI,
)

logger = logging.getLogger(__name__)


async def generate_workflow(description: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Use Claude to generate a workflow definition from a natural language description.

    Args:
        description: Natural language description of the business process.
        context: Additional context (service_type, client_type, etc.).

    Returns:
        A structured workflow definition dict.
    """
    context_str = json.dumps(context or {}, indent=2, default=str)
    user_message = WORKFLOW_GENERATION_USER.format(
        description=description,
        context=context_str,
    )

    result = await claude_client.generate_json(
        system_prompt=WORKFLOW_GENERATION_SYSTEM,
        user_message=user_message,
        max_tokens=4096,
        temperature=0.3,
    )

    # Validate structure (name + steps required). Raise loudly on bad output
    # rather than silently shipping a broken workflow.
    try:
        workflow = WorkflowAI.model_validate(result)
    except ValidationError as exc:
        logger.error("AI-generated workflow failed validation: %s", exc)
        raise ValueError(f"AI-generated workflow is invalid: {exc}") from exc

    # Backfill step name/order from index when the model omitted them.
    for i, step in enumerate(workflow.steps):
        if not step.name:
            step.name = f"Step {i + 1}"
        if step.order is None:
            step.order = i

    logger.info("Generated workflow '%s' with %d steps", workflow.name, len(workflow.steps))
    return workflow.model_dump()


async def classify_document(ocr_text: str) -> dict[str, Any]:
    """Use Claude to classify a document based on OCR text.

    Args:
        ocr_text: Extracted text from OCR processing.

    Returns:
        Classification result with category, confidence, reasoning, and metadata.
    """
    if not ocr_text or len(ocr_text.strip()) < 10:
        return {
            "category": "other",
            "confidence": 0.0,
            "reasoning": "Insufficient text for classification",
            "extracted_metadata": {},
            "language_detected": "unknown",
        }

    # Truncate very long text to fit context window
    truncated = ocr_text[:8000] if len(ocr_text) > 8000 else ocr_text

    user_message = DOCUMENT_CLASSIFICATION_USER.format(ocr_text=truncated)

    result = await claude_client.generate_json(
        system_prompt=DOCUMENT_CLASSIFICATION_SYSTEM,
        user_message=user_message,
        max_tokens=1024,
        temperature=0.1,
    )

    # Validate the AI output. Classification runs in a background OCR pipeline,
    # so on malformed output we log the error and fall back to a safe "other"
    # result instead of crashing the task — but the failure is no longer silent.
    try:
        classification = DocumentClassificationAI.model_validate(result)
    except ValidationError as exc:
        logger.error(
            "Document classification failed validation, using fallback: %s", exc
        )
        classification = DocumentClassificationAI(
            reasoning="AI classification returned malformed output"
        )

    logger.info(
        "Document classified as '%s' with confidence %.2f",
        classification.category,
        classification.confidence,
    )
    return classification.model_dump()


async def assess_eligibility(intake_data: dict[str, Any]) -> dict[str, Any]:
    """Use Claude to assess a client's eligibility for services.

    Args:
        intake_data: Client intake form data.

    Returns:
        Eligibility assessment with services, recommendations, risk factors.
    """
    user_message = ELIGIBILITY_USER.format(
        intake_data=json.dumps(intake_data, indent=2, default=str)
    )

    result = await claude_client.generate_json(
        system_prompt=ELIGIBILITY_SYSTEM,
        user_message=user_message,
        max_tokens=4096,
        temperature=0.2,
    )

    # Eligibility drives client service decisions, so malformed output must not
    # be masked into an empty/"ineligible" result — raise so the caller knows.
    try:
        assessment = EligibilityAssessmentAI.model_validate(result)
    except ValidationError as exc:
        logger.error("Eligibility assessment failed validation: %s", exc)
        raise ValueError(f"AI eligibility assessment is invalid: {exc}") from exc

    logger.info(
        "Eligibility assessment: %d eligible services, confidence %.2f",
        len(assessment.eligible_services),
        assessment.confidence_score,
    )
    return assessment.model_dump()


async def suggest_routing(
    task_details: dict[str, Any],
    staff_details: list[dict[str, Any]],
    client_details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Use Claude to intelligently route a task to the best staff member.

    Args:
        task_details: Information about the task/case needing assignment.
        staff_details: List of available staff with roles, workload, skills.
        client_details: Optional client information for matching.

    Returns:
        Routing recommendation with staff ID, confidence, and reasoning.
    """
    user_message = TASK_ROUTING_USER.format(
        task_details=json.dumps(task_details, indent=2, default=str),
        staff_details=json.dumps(staff_details, indent=2, default=str),
        client_details=json.dumps(client_details or {}, indent=2, default=str),
    )

    result = await claude_client.generate_json(
        system_prompt=TASK_ROUTING_SYSTEM,
        user_message=user_message,
        max_tokens=1024,
        temperature=0.2,
    )

    # Routing is advisory; on malformed output log and return an empty (but
    # validated) recommendation so the caller can fall back to manual routing.
    try:
        routing = TaskRoutingAI.model_validate(result)
    except ValidationError as exc:
        logger.error(
            "Task routing failed validation, returning no recommendation: %s", exc
        )
        routing = TaskRoutingAI(reasoning="AI routing returned malformed output")

    logger.info(
        "Task routing: recommended %s with confidence %.2f",
        routing.recommended_staff_id,
        routing.confidence,
    )
    return routing.model_dump()
