"""Tests for app/services/ai_service.py — Claude client is fully mocked."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.services.ai_service import (
    assess_eligibility,
    classify_document,
    generate_workflow,
    suggest_routing,
)

_MODULE = "app.services.ai_service"


# ── classify_document ─────────────────────────────────────────────────────────

class TestClassifyDocument:
    async def test_empty_text_returns_early_without_api_call(self):
        with patch(f"{_MODULE}.claude_client") as mock_client:
            result = await classify_document("")
        mock_client.generate_json.assert_not_called()
        assert result["category"] == "other"
        assert result["confidence"] == 0.0

    async def test_short_text_below_threshold_returns_early(self):
        with patch(f"{_MODULE}.claude_client") as mock_client:
            result = await classify_document("hi")
        mock_client.generate_json.assert_not_called()
        assert result["category"] == "other"

    async def test_long_text_is_truncated_to_8000_chars(self):
        long_text = "word " * 5000  # >> 8000 chars

        with patch(f"{_MODULE}.claude_client") as mock_client:
            mock_client.generate_json = AsyncMock(
                return_value={"category": "passport", "confidence": 0.95}
            )
            await classify_document(long_text)

        called_with = mock_client.generate_json.call_args
        user_message = called_with.kwargs.get("user_message") or called_with.args[1]
        assert len(user_message) <= 8500  # prompt template wraps the truncated text

    async def test_missing_fields_get_defaults(self):
        with patch(f"{_MODULE}.claude_client") as mock_client:
            mock_client.generate_json = AsyncMock(
                return_value={"category": "visa"}  # minimal API response
            )
            result = await classify_document("This is a valid visa document with enough text")

        assert result["confidence"] == 0.0
        assert result["reasoning"] == ""
        assert result["extracted_metadata"] == {}
        assert result["language_detected"] == "unknown"

    async def test_successful_classification_preserves_api_values(self):
        api_response = {
            "category": "passport",
            "confidence": 0.97,
            "reasoning": "Contains typical passport fields",
            "extracted_metadata": {"country": "US"},
            "language_detected": "en",
        }
        with patch(f"{_MODULE}.claude_client") as mock_client:
            mock_client.generate_json = AsyncMock(return_value=api_response)
            result = await classify_document("Passport number A12345678 issued by USA")

        assert result["category"] == "passport"
        assert result["confidence"] == 0.97


# ── generate_workflow ─────────────────────────────────────────────────────────

class TestGenerateWorkflow:
    async def test_raises_on_missing_name_field(self):
        with patch(f"{_MODULE}.claude_client") as mock_client:
            mock_client.generate_json = AsyncMock(
                return_value={"steps": []}  # missing "name"
            )
            with pytest.raises(ValueError, match="missing fields"):
                await generate_workflow("Send welcome email to new clients")

    async def test_raises_on_missing_steps_field(self):
        with patch(f"{_MODULE}.claude_client") as mock_client:
            mock_client.generate_json = AsyncMock(
                return_value={"name": "Welcome Workflow"}  # missing "steps"
            )
            with pytest.raises(ValueError, match="missing fields"):
                await generate_workflow("Send welcome email")

    async def test_step_missing_name_gets_default(self):
        with patch(f"{_MODULE}.claude_client") as mock_client:
            mock_client.generate_json = AsyncMock(
                return_value={
                    "name": "Onboarding",
                    "steps": [{"step_type": "action", "order": 0}],
                }
            )
            result = await generate_workflow("Onboard new client")

        assert result["steps"][0]["name"] == "Step 1"

    async def test_step_missing_step_type_gets_default(self):
        with patch(f"{_MODULE}.claude_client") as mock_client:
            mock_client.generate_json = AsyncMock(
                return_value={
                    "name": "Onboarding",
                    "steps": [{"name": "Send email", "order": 0}],
                }
            )
            result = await generate_workflow("Onboard new client")

        assert result["steps"][0]["step_type"] == "action"

    async def test_step_missing_order_gets_index(self):
        with patch(f"{_MODULE}.claude_client") as mock_client:
            mock_client.generate_json = AsyncMock(
                return_value={
                    "name": "Onboarding",
                    "steps": [
                        {"name": "Step A", "step_type": "action"},
                        {"name": "Step B", "step_type": "condition"},
                    ],
                }
            )
            result = await generate_workflow("Two-step workflow")

        assert result["steps"][0]["order"] == 0
        assert result["steps"][1]["order"] == 1

    async def test_context_passed_to_api(self):
        with patch(f"{_MODULE}.claude_client") as mock_client:
            mock_client.generate_json = AsyncMock(
                return_value={"name": "Immigration Flow", "steps": []}
            )
            await generate_workflow(
                "Process immigration case", context={"service_type": "immigration"}
            )

        user_msg = mock_client.generate_json.call_args.kwargs.get("user_message") or \
                   mock_client.generate_json.call_args.args[1]
        assert "immigration" in user_msg


# ── assess_eligibility ────────────────────────────────────────────────────────

class TestAssessEligibility:
    async def test_missing_fields_get_defaults(self):
        with patch(f"{_MODULE}.claude_client") as mock_client:
            mock_client.generate_json = AsyncMock(return_value={})
            result = await assess_eligibility({"name": "John"})

        assert result["eligible_services"] == []
        assert result["ineligible_services"] == []
        assert result["recommendations"] == []
        assert result["risk_factors"] == []
        assert result["confidence_score"] == 0.0
        assert result["reasoning"] == ""

    async def test_api_values_preserved(self):
        api_response = {
            "eligible_services": ["legal_aid", "housing"],
            "ineligible_services": ["citizenship"],
            "recommendations": ["Apply for asylum"],
            "risk_factors": ["undocumented"],
            "confidence_score": 0.85,
            "reasoning": "Based on immigration status",
        }
        with patch(f"{_MODULE}.claude_client") as mock_client:
            mock_client.generate_json = AsyncMock(return_value=api_response)
            result = await assess_eligibility({"immigration_status": "undocumented"})

        assert result["eligible_services"] == ["legal_aid", "housing"]
        assert result["confidence_score"] == 0.85


# ── suggest_routing ───────────────────────────────────────────────────────────

class TestSuggestRouting:
    async def test_missing_fields_get_defaults(self):
        with patch(f"{_MODULE}.claude_client") as mock_client:
            mock_client.generate_json = AsyncMock(return_value={})
            result = await suggest_routing(
                task_details={"type": "follow_up"},
                staff_details=[],
            )

        assert result["recommended_staff_id"] is None
        assert result["confidence"] == 0.0
        assert result["reasoning"] == ""
        assert result["alternative_staff_ids"] == []
        assert result["routing_factors"] == {}

    async def test_api_response_preserved(self):
        staff_id = "abc-123"
        api_response = {
            "recommended_staff_id": staff_id,
            "confidence": 0.9,
            "reasoning": "Best language match",
            "alternative_staff_ids": ["def-456"],
            "routing_factors": {"language_match": True},
        }
        with patch(f"{_MODULE}.claude_client") as mock_client:
            mock_client.generate_json = AsyncMock(return_value=api_response)
            result = await suggest_routing(
                task_details={"type": "translation"},
                staff_details=[{"id": staff_id, "language": "Spanish"}],
            )

        assert result["recommended_staff_id"] == staff_id
        assert result["confidence"] == 0.9
