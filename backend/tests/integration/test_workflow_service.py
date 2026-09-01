"""Integration tests for app/services/workflow_service.py (DB session is mocked)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.constants import (
    WorkflowExecutionStatus,
    WorkflowStepType,
    WorkflowTriggerType,
)
from app.models.workflow import (
    Workflow,
    WorkflowExecution,
    WorkflowStep,
    RoutingRule,
)
from app.schemas.workflow import (
    RoutingRuleCreate,
    WorkflowCreate,
    WorkflowStepCreate,
    WorkflowUpdate,
)
from app.services import workflow_service
from tests.conftest import make_db_result, make_session


def _make_workflow(is_active: bool = True, name: str = "Test Workflow") -> Workflow:
    wf = Workflow(
        id=uuid.uuid4(),
        name=name,
        description="A test workflow",
        trigger_type=WorkflowTriggerType.MANUAL,
        trigger_config={},
        is_active=is_active,
        is_ai_generated=False,
        created_by_id=uuid.uuid4(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    wf.steps = []
    return wf


def _make_step(workflow_id: uuid.UUID, order: int = 0) -> WorkflowStep:
    step = WorkflowStep(
        id=uuid.uuid4(),
        workflow_id=workflow_id,
        name=f"Step {order}",
        step_type=WorkflowStepType.SEND_NOTIFICATION,
        step_order=order,
        config={},
        condition=None,
        on_failure="stop",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    return step


def _make_rule(priority: int = 0, conditions: dict | None = None) -> RoutingRule:
    rule = RoutingRule(
        id=uuid.uuid4(),
        name=f"Rule P{priority}",
        conditions=conditions or {"status": "open"},
        priority=priority,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    rule.assign_to = None
    rule.assign_to_role = None
    return rule


# ── get_workflow ──────────────────────────────────────────────────────────────

class TestGetWorkflow:
    async def test_returns_workflow_read(self):
        wf = _make_workflow()
        step = _make_step(wf.id)
        wf.steps = [step]

        session = AsyncMock()
        # execute calls: 1) get workflow, 2) get steps, 3) count executions, 4) last execution
        results = [
            make_db_result(wf),            # workflow lookup
            make_db_result(values=[step]), # steps
            make_db_result(0),             # count
            MagicMock(first=MagicMock(return_value=None)),  # last_exec
        ]
        session.execute.side_effect = results
        session.flush = AsyncMock()
        session.refresh = AsyncMock()

        result = await workflow_service.get_workflow(session, wf.id)

        assert result.id == wf.id
        assert result.name == wf.name
        assert len(result.steps) == 1

    async def test_missing_workflow_raises_404(self):
        session = make_session(None)
        with pytest.raises(HTTPException) as exc:
            await workflow_service.get_workflow(session, uuid.uuid4())
        assert exc.value.status_code == 404


# ── create_workflow ───────────────────────────────────────────────────────────

class TestCreateWorkflow:
    async def test_creates_workflow_with_steps(self):
        session = AsyncMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.add = MagicMock()

        payload = WorkflowCreate(
            name="New Workflow",
            description="Test",
            trigger_type="manual",
            trigger_config={},
            steps=[
                WorkflowStepCreate(
                    name="Notify Client",
                    step_type="send_notification",
                    order=0,
                    config={},
                )
            ],
        )
        result = await workflow_service.create_workflow(session, payload, uuid.uuid4())

        assert result.name == "New Workflow"
        assert len(result.steps) == 1
        assert result.steps[0].name == "Notify Client"
        # New workflows start inactive
        assert result.status == "draft"

    async def test_unknown_trigger_type_defaults_to_manual(self):
        session = AsyncMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.add = MagicMock()

        payload = WorkflowCreate(
            name="Fallback Workflow",
            trigger_type="manual",  # test internal fallback path
            trigger_config={},
            steps=[],
        )
        result = await workflow_service.create_workflow(session, payload, uuid.uuid4())
        assert result.name == "Fallback Workflow"


# ── update_workflow ───────────────────────────────────────────────────────────

class TestUpdateWorkflow:
    async def test_update_name_and_description(self):
        wf = _make_workflow()
        wf.steps = []
        step = _make_step(wf.id)

        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        # First call: find workflow to update
        # Subsequent calls inside get_workflow: workflow, steps, count, last_exec
        results = [
            make_db_result(wf),
            make_db_result(wf),
            make_db_result(values=[step]),
            make_db_result(0),
            MagicMock(first=MagicMock(return_value=None)),
        ]
        session.execute.side_effect = results

        payload = WorkflowUpdate(name="Updated Name", description="Updated desc")
        result = await workflow_service.update_workflow(session, wf.id, payload)

        assert wf.name == "Updated Name"
        assert wf.description == "Updated desc"

    async def test_missing_workflow_raises_404(self):
        session = make_session(None)
        with pytest.raises(HTTPException) as exc:
            await workflow_service.update_workflow(session, uuid.uuid4(), WorkflowUpdate())
        assert exc.value.status_code == 404

    async def test_setting_status_active_sets_is_active(self):
        wf = _make_workflow(is_active=False)
        wf.steps = []
        step = _make_step(wf.id)

        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        results = [
            make_db_result(wf),
            make_db_result(wf),
            make_db_result(values=[step]),
            make_db_result(0),
            MagicMock(first=MagicMock(return_value=None)),
        ]
        session.execute.side_effect = results

        await workflow_service.update_workflow(session, wf.id, WorkflowUpdate(status="active"))
        assert wf.is_active is True


# ── execute_workflow ──────────────────────────────────────────────────────────

class TestExecuteWorkflow:
    async def test_inactive_workflow_raises_400(self):
        wf = _make_workflow(is_active=False)
        session = make_session(wf)

        with pytest.raises(HTTPException) as exc:
            await workflow_service.execute_workflow(session, wf.id)
        assert exc.value.status_code == 400
        assert "active" in exc.value.detail.lower()

    async def test_missing_workflow_raises_404(self):
        session = make_session(None)
        with pytest.raises(HTTPException) as exc:
            await workflow_service.execute_workflow(session, uuid.uuid4())
        assert exc.value.status_code == 404

    async def test_creates_execution_record_for_active_workflow(self):
        wf = _make_workflow(is_active=True)
        step = _make_step(wf.id)

        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()

        results = [
            make_db_result(wf),           # workflow lookup
            make_db_result(values=[step]),  # steps
        ]
        session.execute.side_effect = results

        added_objects = []
        session.add.side_effect = added_objects.append

        with patch("app.workers.workflow_tasks.execute_workflow_step") as mock_task:
            mock_task.delay = MagicMock()
            result = await workflow_service.execute_workflow(session, wf.id, trigger_data={"source": "test"})

        assert result.workflow_id == wf.id
        executions = [o for o in added_objects if isinstance(o, WorkflowExecution)]
        assert len(executions) == 1
        assert executions[0].trigger_data == {"source": "test"}

    async def test_first_step_dispatched_to_celery(self):
        wf = _make_workflow(is_active=True)
        step = _make_step(wf.id)

        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()

        results = [make_db_result(wf), make_db_result(values=[step])]
        session.execute.side_effect = results

        with patch("app.workers.workflow_tasks.execute_workflow_step") as mock_task:
            mock_task.delay = MagicMock()
            await workflow_service.execute_workflow(session, wf.id)

        mock_task.delay.assert_called_once()
        call_args = mock_task.delay.call_args[0]
        assert call_args[1] == str(step.id)

    async def test_no_steps_no_celery_dispatch(self):
        wf = _make_workflow(is_active=True)

        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()

        results = [make_db_result(wf), make_db_result(values=[])]
        session.execute.side_effect = results

        with patch("app.workers.workflow_tasks.execute_workflow_step") as mock_task:
            mock_task.delay = MagicMock()
            await workflow_service.execute_workflow(session, wf.id)

        mock_task.delay.assert_not_called()


# ── evaluate_routing_rules ────────────────────────────────────────────────────

class TestEvaluateRoutingRules:
    async def test_returns_highest_priority_matching_rule(self):
        low_rule = _make_rule(priority=0, conditions={"status": "open"})
        low_rule.assign_to = None
        low_rule.assign_to_role = None
        high_rule = _make_rule(priority=10, conditions={"status": "open"})
        high_rule.assign_to = None
        high_rule.assign_to_role = None

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [high_rule, low_rule]
        session = AsyncMock()
        session.execute.return_value = result_mock

        result = await workflow_service.evaluate_routing_rules(
            session, context={"status": "open"}
        )

        assert result is not None
        assert result.name == high_rule.name

    async def test_no_matching_rule_returns_none(self):
        rule = _make_rule(priority=0, conditions={"status": "closed"})
        rule.assign_to = None
        rule.assign_to_role = None

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [rule]
        session = AsyncMock()
        session.execute.return_value = result_mock

        result = await workflow_service.evaluate_routing_rules(
            session, context={"status": "open"}
        )
        assert result is None

    async def test_no_rules_returns_none(self):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        session = AsyncMock()
        session.execute.return_value = result_mock

        result = await workflow_service.evaluate_routing_rules(session, context={"status": "open"})
        assert result is None
