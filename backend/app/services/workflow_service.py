"""Workflow engine service: CRUD, execution, and AI generation."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import WorkflowExecutionStatus, WorkflowStepType, WorkflowTriggerType
from app.core.pagination import PaginatedResponse, PaginationParams, paginate
from app.models.workflow import (
    RoutingRule,
    Workflow,
    WorkflowExecution,
    WorkflowStep,
    WorkflowStepLog,
)
from app.schemas.workflow import (
    ExecutionStatus,
    RoutingRuleCreate,
    RoutingRuleRead,
    StepLogRead,
    StepLogStatus,
    WorkflowCreate,
    WorkflowExecutionRead,
    WorkflowRead,
    WorkflowStepCreate,
    WorkflowStepRead,
    WorkflowUpdate,
)

logger = logging.getLogger(__name__)


def _to_step_read(step: WorkflowStep) -> WorkflowStepRead:
    """Map WorkflowStep model to WorkflowStepRead schema."""
    return WorkflowStepRead(
        id=step.id,
        workflow_id=step.workflow_id,
        name=step.name,
        step_type=step.step_type.value,
        order=step.step_order,
        config=step.config or {},
        condition=step.condition,
        timeout_seconds=None,
        retry_count=0,
        on_failure=step.on_failure,
        created_at=step.created_at,
    )


def _to_workflow_read(
    workflow: Workflow,
    steps: list[WorkflowStep] | None = None,
    executions_count: int = 0,
    last_executed_at: datetime | None = None,
) -> WorkflowRead:
    """Map Workflow model to WorkflowRead schema."""
    wf_status = "active" if workflow.is_active else "draft"
    step_reads = [_to_step_read(s) for s in (steps or workflow.steps or [])]

    return WorkflowRead(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        status=wf_status,
        trigger_type=workflow.trigger_type.value,
        trigger_config=workflow.trigger_config or {},
        steps=step_reads,
        created_by=workflow.created_by_id or UUID("00000000-0000-0000-0000-000000000000"),
        executions_count=executions_count,
        last_executed_at=last_executed_at,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at,
    )


# --- Workflow CRUD ---

async def create_workflow(
    session: AsyncSession, payload: WorkflowCreate, created_by: UUID
) -> WorkflowRead:
    """Create a workflow with its steps."""
    # Map schema trigger_type to model WorkflowTriggerType
    try:
        model_trigger = WorkflowTriggerType(payload.trigger_type.value)
    except ValueError:
        model_trigger = WorkflowTriggerType.MANUAL

    workflow = Workflow(
        name=payload.name,
        description=payload.description,
        trigger_type=model_trigger,
        trigger_config=payload.trigger_config,
        is_active=False,  # Start as draft/inactive
        is_ai_generated=False,
        created_by_id=created_by,
    )
    session.add(workflow)
    await session.flush()

    steps = []
    for step_data in payload.steps:
        # Map schema step_type to model WorkflowStepType
        try:
            model_step_type = WorkflowStepType(step_data.step_type.value)
        except ValueError:
            model_step_type = WorkflowStepType.SEND_NOTIFICATION

        step = WorkflowStep(
            workflow_id=workflow.id,
            name=step_data.name,
            step_type=model_step_type,
            step_order=step_data.order,
            config=step_data.config,
            condition=step_data.condition,
            on_failure=step_data.on_failure,
        )
        session.add(step)
        steps.append(step)

    await session.flush()
    for step in steps:
        await session.refresh(step)

    await session.refresh(workflow)

    return _to_workflow_read(workflow, steps=steps, executions_count=0)


async def get_workflow(session: AsyncSession, workflow_id: UUID) -> WorkflowRead:
    """Get a workflow with its steps."""
    result = await session.execute(
        select(Workflow).where(Workflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    if workflow is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    steps_result = await session.execute(
        select(WorkflowStep)
        .where(WorkflowStep.workflow_id == workflow_id)
        .order_by(WorkflowStep.step_order)
    )
    steps = steps_result.scalars().all()

    exec_count_result = await session.execute(
        select(func.count(WorkflowExecution.id))
        .where(WorkflowExecution.workflow_id == workflow_id)
    )
    executions_count = exec_count_result.scalar_one()

    last_exec_result = await session.execute(
        select(WorkflowExecution.started_at)
        .where(WorkflowExecution.workflow_id == workflow_id)
        .order_by(WorkflowExecution.started_at.desc())
        .limit(1)
    )
    last_row = last_exec_result.first()
    last_executed_at = last_row[0] if last_row else None

    return _to_workflow_read(workflow, steps=list(steps), executions_count=executions_count, last_executed_at=last_executed_at)


async def list_workflows(
    session: AsyncSession, pagination: PaginationParams, status_filter: str | None = None
) -> PaginatedResponse[WorkflowRead]:
    query = select(Workflow)
    if status_filter:
        if status_filter == "active":
            query = query.where(Workflow.is_active == True)
        elif status_filter in ("draft", "paused", "archived"):
            query = query.where(Workflow.is_active == False)
    query = query.order_by(Workflow.created_at.desc())
    result = await paginate(session, query, pagination)
    result.items = [_to_workflow_read(wf) for wf in result.items]
    return result


async def update_workflow(
    session: AsyncSession, workflow_id: UUID, payload: WorkflowUpdate
) -> WorkflowRead:
    result = await session.execute(
        select(Workflow).where(Workflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    if workflow is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    update_data = payload.model_dump(exclude_unset=True)

    if "status" in update_data and update_data["status"] is not None:
        status_val = update_data.pop("status").value if hasattr(update_data.get("status"), "value") else update_data.pop("status")
        workflow.is_active = status_val == "active"

    if "trigger_type" in update_data and update_data["trigger_type"] is not None:
        try:
            workflow.trigger_type = WorkflowTriggerType(update_data.pop("trigger_type").value)
        except (ValueError, AttributeError):
            update_data.pop("trigger_type", None)

    for field in ("name", "description", "trigger_config"):
        if field in update_data and update_data[field] is not None:
            setattr(workflow, field, update_data[field])

    session.add(workflow)
    await session.flush()
    return await get_workflow(session, workflow_id)


async def delete_workflow(session: AsyncSession, workflow_id: UUID) -> None:
    result = await session.execute(
        select(Workflow).where(Workflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    if workflow is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    # Deactivate instead of soft-delete (no is_deleted on Workflow)
    workflow.is_active = False
    session.add(workflow)


# --- Execution ---

def _to_execution_read(execution: WorkflowExecution, workflow_name: str | None = None) -> WorkflowExecutionRead:
    """Map WorkflowExecution model to schema."""
    return WorkflowExecutionRead(
        id=execution.id,
        workflow_id=execution.workflow_id,
        workflow_name=workflow_name or (execution.workflow.name if execution.workflow else None),
        status=execution.status.value,
        trigger_data=execution.trigger_data or {},
        result=execution.result_data,
        error_message=execution.error_message,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        current_step=execution.current_step,
    )


async def execute_workflow(
    session: AsyncSession,
    workflow_id: UUID,
    trigger_data: dict[str, Any] | None = None,
    triggered_by: UUID | None = None,
) -> WorkflowExecutionRead:
    """Start executing a workflow. Steps are dispatched to Celery."""
    wf_result = await session.execute(
        select(Workflow).where(Workflow.id == workflow_id)
    )
    workflow = wf_result.scalar_one_or_none()
    if workflow is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    if not workflow.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow must be active to execute",
        )

    execution = WorkflowExecution(
        workflow_id=workflow_id,
        status=WorkflowExecutionStatus.RUNNING,
        triggered_by_id=triggered_by,
        trigger_data=trigger_data or {},
        started_at=datetime.now(timezone.utc),
        current_step=0,
    )
    session.add(execution)
    await session.flush()
    await session.refresh(execution)

    # Get steps
    steps_result = await session.execute(
        select(WorkflowStep)
        .where(WorkflowStep.workflow_id == workflow_id)
        .order_by(WorkflowStep.step_order)
    )
    steps = steps_result.scalars().all()

    # Create step logs
    for step in steps:
        step_log = WorkflowStepLog(
            execution_id=execution.id,
            step_id=step.id,
            status=WorkflowExecutionStatus.PAUSED,  # Pending
            started_at=datetime.now(timezone.utc),
        )
        session.add(step_log)

    await session.flush()

    # Dispatch first step to Celery
    if steps:
        try:
            from app.workers.workflow_tasks import execute_workflow_step
            execute_workflow_step.delay(str(execution.id), str(steps[0].id))
        except Exception:
            logger.warning("Could not dispatch workflow step to Celery for execution %s", execution.id)

    return _to_execution_read(execution, workflow_name=workflow.name)


async def get_execution(session: AsyncSession, execution_id: UUID) -> WorkflowExecutionRead:
    result = await session.execute(
        select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
    )
    execution = result.scalar_one_or_none()
    if execution is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execution not found")

    return _to_execution_read(execution)


async def list_executions(
    session: AsyncSession,
    pagination: PaginationParams,
    workflow_id: UUID | None = None,
    status_filter: str | None = None,
) -> PaginatedResponse[WorkflowExecutionRead]:
    query = select(WorkflowExecution)
    if workflow_id:
        query = query.where(WorkflowExecution.workflow_id == workflow_id)
    if status_filter:
        try:
            query = query.where(WorkflowExecution.status == WorkflowExecutionStatus(status_filter))
        except ValueError:
            pass
    query = query.order_by(WorkflowExecution.started_at.desc())
    result = await paginate(session, query, pagination)
    result.items = [_to_execution_read(e) for e in result.items]
    return result


async def get_step_logs(
    session: AsyncSession, execution_id: UUID
) -> list[StepLogRead]:
    result = await session.execute(
        select(WorkflowStepLog)
        .where(WorkflowStepLog.execution_id == execution_id)
        .order_by(WorkflowStepLog.started_at.asc().nulls_last())
    )
    logs = result.scalars().all()

    reads = []
    for log in logs:
        step_name = log.step.name if log.step else None
        duration_ms = None
        if log.started_at and log.completed_at:
            duration_ms = int((log.completed_at - log.started_at).total_seconds() * 1000)

        reads.append(StepLogRead(
            id=log.id,
            execution_id=log.execution_id,
            step_id=log.step_id,
            step_name=step_name,
            status=log.status.value,
            input_data=log.input_data,
            output_data=log.output_data,
            error_message=log.error_message,
            started_at=log.started_at,
            completed_at=log.completed_at,
            duration_ms=duration_ms,
        ))
    return reads


# --- Routing Rules ---

def _to_routing_rule_read(rule: RoutingRule) -> RoutingRuleRead:
    """Map RoutingRule model to schema."""
    action = {}
    if rule.assign_to_id:
        action["assign_to_user"] = str(rule.assign_to_id)
    if rule.assign_to_role_id:
        action["assign_to_role"] = str(rule.assign_to_role_id)

    return RoutingRuleRead(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        conditions=rule.conditions,
        action=action,
        priority=rule.priority,
        is_active=rule.is_active,
        created_at=rule.created_at,
        updated_at=rule.updated_at,
    )


async def create_routing_rule(session: AsyncSession, payload: RoutingRuleCreate) -> RoutingRuleRead:
    # Extract assign_to from action dict
    assign_to_id = None
    assign_to_role_id = None
    if payload.action:
        assign_to_str = payload.action.get("assign_to_user")
        if assign_to_str:
            try:
                assign_to_id = UUID(assign_to_str)
            except (ValueError, TypeError):
                pass
        role_str = payload.action.get("assign_to_role")
        if role_str:
            try:
                assign_to_role_id = UUID(role_str)
            except (ValueError, TypeError):
                pass

    rule = RoutingRule(
        name=payload.name,
        description=payload.description,
        conditions=payload.conditions,
        assign_to_id=assign_to_id,
        assign_to_role_id=assign_to_role_id,
        priority=payload.priority,
        is_active=payload.is_active,
    )
    session.add(rule)
    await session.flush()
    await session.refresh(rule)
    return _to_routing_rule_read(rule)


async def list_routing_rules(
    session: AsyncSession, pagination: PaginationParams, active_only: bool = True
) -> PaginatedResponse[RoutingRuleRead]:
    query = select(RoutingRule)
    if active_only:
        query = query.where(RoutingRule.is_active == True)
    query = query.order_by(RoutingRule.priority.desc())
    result = await paginate(session, query, pagination)
    result.items = [_to_routing_rule_read(r) for r in result.items]
    return result


async def evaluate_routing_rules(
    session: AsyncSession, context: dict[str, Any]
) -> RoutingRuleRead | None:
    """Evaluate routing rules against context and return the first matching rule."""
    rules_result = await session.execute(
        select(RoutingRule)
        .where(RoutingRule.is_active == True)
        .order_by(RoutingRule.priority.desc())
    )
    rules = rules_result.scalars().all()

    for rule in rules:
        if _evaluate_conditions(rule.conditions, context):
            return _to_routing_rule_read(rule)

    return None


def _evaluate_conditions(conditions: dict[str, Any], context: dict[str, Any]) -> bool:
    """Simple condition evaluator for routing rules."""
    for field, criteria in conditions.items():
        context_value = context.get(field)
        if context_value is None:
            return False

        if isinstance(criteria, dict):
            operator = criteria.get("operator", "eq")
            expected = criteria.get("value")

            if operator == "eq" and context_value != expected:
                return False
            elif operator == "ne" and context_value == expected:
                return False
            elif operator == "gt" and not (context_value > expected):
                return False
            elif operator == "lt" and not (context_value < expected):
                return False
            elif operator == "contains" and expected not in str(context_value):
                return False
            elif operator == "in" and context_value not in expected:
                return False
        else:
            # Simple equality check
            if context_value != criteria:
                return False

    return True
