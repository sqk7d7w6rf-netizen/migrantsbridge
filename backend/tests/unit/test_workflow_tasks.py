"""
Tests for workflow Celery task logic.

We test the internal async helpers (_execute_step_action, _advance_to_next)
directly — they contain all the business logic.  The Celery wrapper itself is
not called so no broker is needed.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.constants import WorkflowExecutionStatus, WorkflowStepType
from app.workers.workflow_tasks import _advance_to_next, _execute_step_action


def _make_step(step_type: WorkflowStepType = WorkflowStepType.SEND_NOTIFICATION, config: dict | None = None):
    step = MagicMock()
    step.id = uuid.uuid4()
    step.workflow_id = uuid.uuid4()
    step.step_type = step_type
    step.step_order = 0
    step.name = "Test Step"
    step.config = config or {}
    step.on_failure = "stop"
    return step


def _make_execution(trigger_data: dict | None = None):
    execution = MagicMock()
    execution.id = uuid.uuid4()
    execution.trigger_data = trigger_data or {}
    execution.status = WorkflowExecutionStatus.RUNNING
    return execution


def _make_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    return session


# ── _execute_step_action ──────────────────────────────────────────────────────

class TestExecuteStepAction:
    async def test_send_notification_queues_notification(self):
        step = _make_step(
            config={
                "action_type": "send_notification",
                "parameters": {
                    "channel": "in_app",
                    "subject": "Hello",
                    "body": "Test message",
                },
            }
        )
        session = _make_session()
        execution = _make_execution()

        result = await _execute_step_action(session, step, execution)

        assert result["action"] == "send_notification"
        assert result["result"] == "queued"
        session.add.assert_called_once()

    async def test_unknown_action_type_executes_generic(self):
        step = _make_step(config={"action_type": "custom_step", "parameters": {}})
        execution = _make_execution()
        session = _make_session()

        result = await _execute_step_action(session, step, execution)

        assert result["action"] == "custom_step"
        assert result["result"] == "executed"

    async def test_create_case_returns_placeholder(self):
        step = _make_step(config={"action_type": "create_case"})
        session = _make_session()
        execution = _make_execution()

        result = await _execute_step_action(session, step, execution)
        assert result["action"] == "create_case"

    async def test_assign_task_returns_placeholder(self):
        step = _make_step(config={"action_type": "assign_task"})
        session = _make_session()
        execution = _make_execution()

        result = await _execute_step_action(session, step, execution)
        assert result["action"] == "assign_task"

    async def test_request_approval_returns_pending(self):
        step = _make_step(
            config={"action_type": "request_approval", "parameters": {"approver_id": "user-1"}}
        )
        session = _make_session()
        execution = _make_execution()

        result = await _execute_step_action(session, step, execution)
        assert result["result"] == "approval_pending"
        assert result["approver"] == "user-1"

    async def test_update_status_no_op_when_no_case_id(self):
        step = _make_step(
            config={
                "action_type": "update_status",
                "parameters": {"status": "closed_successful"},
            }
        )
        session = _make_session()
        execution = _make_execution(trigger_data={})

        result = await _execute_step_action(session, step, execution)
        assert result["action"] == "update_status"
        assert result["result"] == "no_op"

    async def test_check_eligibility_calls_ai_service(self):
        step = _make_step(
            config={
                "action_type": "check_eligibility",
                "parameters": {"intake_data": {"status": "refugee"}},
            }
        )
        session = _make_session()
        execution = _make_execution()

        mock_assessment = {"eligible_services": ["legal_aid"], "confidence_score": 0.9}
        with patch(
            "app.workers.workflow_tasks.assess_eligibility",
            new=AsyncMock(return_value=mock_assessment),
        ):
            result = await _execute_step_action(session, step, execution)

        assert result["action"] == "check_eligibility"
        assert result["result"] == mock_assessment

    async def test_no_config_falls_back_to_step_type(self):
        step = _make_step(step_type=WorkflowStepType.SEND_NOTIFICATION, config={})
        session = _make_session()
        execution = _make_execution()

        # action_type is inferred from step.step_type.value → "send_notification"
        result = await _execute_step_action(session, step, execution)
        assert result["action"] == "send_notification"


# ── _advance_to_next ──────────────────────────────────────────────────────────

class TestAdvanceToNext:
    async def test_advances_and_dispatches_next_step(self):
        current_step = _make_step()
        current_step.step_order = 0

        next_step = MagicMock()
        next_step.id = uuid.uuid4()
        next_step.step_order = 1

        from unittest.mock import MagicMock as MM
        result_mock = MM()
        result_mock.scalar_one_or_none.return_value = next_step
        session = AsyncMock()
        session.execute.return_value = result_mock
        session.add = MagicMock()

        execution = _make_execution()

        with patch(
            "app.workers.workflow_tasks.execute_workflow_step"
        ) as mock_task:
            mock_task.delay = MagicMock()
            await _advance_to_next(session, execution, current_step)

        mock_task.delay.assert_called_once_with(str(execution.id), str(next_step.id))
        assert execution.current_step == 1

    async def test_marks_execution_complete_when_no_next_step(self):
        current_step = _make_step()
        current_step.step_order = 1

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session = AsyncMock()
        session.execute.return_value = result_mock
        session.add = MagicMock()

        execution = _make_execution()

        with patch("app.workers.workflow_tasks.execute_workflow_step"):
            await _advance_to_next(session, execution, current_step)

        assert execution.status == WorkflowExecutionStatus.COMPLETED
        assert execution.completed_at is not None
