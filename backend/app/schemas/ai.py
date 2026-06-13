"""Pydantic schemas that validate Claude's JSON responses.

These replace the previous `dict.setdefault(...)` pattern, which silently
masked malformed AI output (e.g. a non-numeric ``confidence`` or a missing
``category`` would slip through as a default instead of surfacing an error).
Validating through these models enforces types, clamps confidence scores to a
sane range, and lets the service layer log/raise on bad output instead of
quietly trusting it.

``extra="allow"`` is used so additional fields Claude returns are preserved
rather than dropped.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


def _clamp_unit(value: Any) -> float:
    """Coerce to float and clamp into the [0.0, 1.0] range."""
    return min(max(float(value), 0.0), 1.0)


class WorkflowStepAI(BaseModel):
    """A single step in an AI-generated workflow."""

    model_config = ConfigDict(extra="allow")

    # name/order are optional so the service can backfill from the step index
    # (preserving the previous "fill if missing" behaviour) without being
    # unable to distinguish a real value from a default.
    name: str | None = None
    step_type: str = "action"
    order: int | None = None
    description: str | None = None
    config: dict[str, Any] = {}


class WorkflowAI(BaseModel):
    """An AI-generated workflow definition. ``name`` and ``steps`` are required."""

    model_config = ConfigDict(extra="allow")

    name: str
    steps: list[WorkflowStepAI] = []
    description: str | None = None


class DocumentClassificationAI(BaseModel):
    """Result of AI document classification."""

    model_config = ConfigDict(extra="allow")

    category: str = "other"
    confidence: float = 0.0
    reasoning: str = ""
    extracted_metadata: dict[str, Any] = {}
    language_detected: str = "unknown"

    @field_validator("confidence")
    @classmethod
    def _clamp_confidence(cls, v: Any) -> float:
        return _clamp_unit(v)


class EligibilityAssessmentAI(BaseModel):
    """Result of an AI eligibility assessment."""

    model_config = ConfigDict(extra="allow")

    eligible_services: list[Any] = []
    ineligible_services: list[Any] = []
    recommendations: list[Any] = []
    risk_factors: list[Any] = []
    confidence_score: float = 0.0
    reasoning: str = ""

    @field_validator("confidence_score")
    @classmethod
    def _clamp_confidence(cls, v: Any) -> float:
        return _clamp_unit(v)


class TaskRoutingAI(BaseModel):
    """Result of an AI task-routing recommendation."""

    model_config = ConfigDict(extra="allow")

    recommended_staff_id: str | None = None
    confidence: float = 0.0
    reasoning: str = ""
    alternative_staff_ids: list[Any] = []
    routing_factors: dict[str, Any] = {}

    @field_validator("confidence")
    @classmethod
    def _clamp_confidence(cls, v: Any) -> float:
        return _clamp_unit(v)
