"""Tests for workflow_service._evaluate_conditions — pure function, no DB."""

import pytest

from app.services.workflow_service import _evaluate_conditions


class TestEvaluateConditions:
    # ── Simple equality (dict value, no operator key) ─────────────────────────

    def test_simple_equality_matches(self):
        assert _evaluate_conditions({"status": "open"}, {"status": "open"}) is True

    def test_simple_equality_mismatch(self):
        assert _evaluate_conditions({"status": "open"}, {"status": "closed"}) is False

    def test_missing_field_in_context(self):
        assert _evaluate_conditions({"status": "open"}, {}) is False

    def test_multiple_conditions_all_must_match(self):
        conditions = {"status": "open", "type": "immigration"}
        assert _evaluate_conditions(conditions, {"status": "open", "type": "immigration"}) is True
        assert _evaluate_conditions(conditions, {"status": "open", "type": "legal"}) is False

    # ── eq operator ──────────────────────────────────────────────────────────

    def test_operator_eq_match(self):
        cond = {"priority": {"operator": "eq", "value": "high"}}
        assert _evaluate_conditions(cond, {"priority": "high"}) is True

    def test_operator_eq_mismatch(self):
        cond = {"priority": {"operator": "eq", "value": "high"}}
        assert _evaluate_conditions(cond, {"priority": "low"}) is False

    # ── ne operator ──────────────────────────────────────────────────────────

    def test_operator_ne_different_values(self):
        cond = {"status": {"operator": "ne", "value": "closed"}}
        assert _evaluate_conditions(cond, {"status": "open"}) is True

    def test_operator_ne_same_value(self):
        cond = {"status": {"operator": "ne", "value": "closed"}}
        assert _evaluate_conditions(cond, {"status": "closed"}) is False

    # ── gt / lt operators ────────────────────────────────────────────────────

    def test_operator_gt_greater(self):
        cond = {"age": {"operator": "gt", "value": 18}}
        assert _evaluate_conditions(cond, {"age": 25}) is True

    def test_operator_gt_equal(self):
        cond = {"age": {"operator": "gt", "value": 18}}
        assert _evaluate_conditions(cond, {"age": 18}) is False

    def test_operator_gt_less(self):
        cond = {"age": {"operator": "gt", "value": 18}}
        assert _evaluate_conditions(cond, {"age": 10}) is False

    def test_operator_lt_less(self):
        cond = {"score": {"operator": "lt", "value": 100}}
        assert _evaluate_conditions(cond, {"score": 50}) is True

    def test_operator_lt_equal(self):
        cond = {"score": {"operator": "lt", "value": 100}}
        assert _evaluate_conditions(cond, {"score": 100}) is False

    # ── contains operator ────────────────────────────────────────────────────

    def test_operator_contains_substring_match(self):
        cond = {"notes": {"operator": "contains", "value": "urgent"}}
        assert _evaluate_conditions(cond, {"notes": "This is an urgent case"}) is True

    def test_operator_contains_no_match(self):
        cond = {"notes": {"operator": "contains", "value": "urgent"}}
        assert _evaluate_conditions(cond, {"notes": "Routine processing"}) is False

    # ── in operator ──────────────────────────────────────────────────────────

    def test_operator_in_value_present(self):
        cond = {"status": {"operator": "in", "value": ["open", "in_progress"]}}
        assert _evaluate_conditions(cond, {"status": "open"}) is True

    def test_operator_in_value_absent(self):
        cond = {"status": {"operator": "in", "value": ["open", "in_progress"]}}
        assert _evaluate_conditions(cond, {"status": "closed"}) is False

    # ── Edge cases ────────────────────────────────────────────────────────────

    def test_empty_conditions_always_match(self):
        assert _evaluate_conditions({}, {"any": "value"}) is True

    def test_empty_conditions_empty_context(self):
        assert _evaluate_conditions({}, {}) is True

    def test_numeric_equality(self):
        cond = {"count": 3}
        assert _evaluate_conditions(cond, {"count": 3}) is True
        assert _evaluate_conditions(cond, {"count": 4}) is False

    def test_boolean_condition(self):
        cond = {"is_urgent": True}
        assert _evaluate_conditions(cond, {"is_urgent": True}) is True
        assert _evaluate_conditions(cond, {"is_urgent": False}) is False
