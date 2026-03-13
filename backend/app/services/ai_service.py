"""AI service: Claude API integration for workflow generation, document classification, eligibility assessment, and routing."""

from __future__ import annotations

import json
import logging
from typing import Any

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

    # Validate required fields
    required_fields = {"name", "steps"}
    missing = required_fields - set(result.keys())
    if missing:
        raise ValueError(f"AI-generated workflow missing fields: {missing}")

    # Ensure steps have required fields
    for i, step in enumerate(result.get("steps", [])):
        if "name" not in step:
            step["name"] = f"Step {i + 1}"
        if "step_type" not in step:
            step["step_type"] = "action"
        if "order" not in step:
            step["order"] = i

    logger.info("Generated workflow '%s' with %d steps", result.get("name"), len(result.get("steps", [])))
    return result


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

    # Ensure required fields
    result.setdefault("category", "other")
    result.setdefault("confidence", 0.0)
    result.setdefault("reasoning", "")
    result.setdefault("extracted_metadata", {})
    result.setdefault("language_detected", "unknown")

    logger.info(
        "Document classified as '%s' with confidence %.2f",
        result["category"],
        result["confidence"],
    )
    return result


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

    # Ensure required fields
    result.setdefault("eligible_services", [])
    result.setdefault("ineligible_services", [])
    result.setdefault("recommendations", [])
    result.setdefault("risk_factors", [])
    result.setdefault("confidence_score", 0.0)
    result.setdefault("reasoning", "")

    logger.info(
        "Eligibility assessment: %d eligible services, confidence %.2f",
        len(result["eligible_services"]),
        result["confidence_score"],
    )
    return result


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

    result.setdefault("recommended_staff_id", None)
    result.setdefault("confidence", 0.0)
    result.setdefault("reasoning", "")
    result.setdefault("alternative_staff_ids", [])
    result.setdefault("routing_factors", {})

    logger.info(
        "Task routing: recommended %s with confidence %.2f",
        result["recommended_staff_id"],
        result["confidence"],
    )
    return result
