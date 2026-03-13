"""Celery tasks for workflow step execution."""

from __future__ import annotations

import asyncio
import logging
import time
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
def execute_workflow_step(self, execution_id: str, step_id: str) -> dict:
    """Execute a single workflow step and advance to the next one."""
    logger.info("Executing workflow step %s (execution %s)", step_id, execution_id)

    async def _execute():
        from uuid import UUID

        from sqlalchemy import select

        from app.constants import WorkflowExecutionStatus
        from app.core.database import async_session_factory
        from app.models.workflow import (
            Workflow,
            WorkflowExecution,
            WorkflowStep,
            WorkflowStepLog,
        )

        async with async_session_factory() as session:
            # Load execution and step
            exec_result = await session.execute(
                select(WorkflowExecution).where(WorkflowExecution.id == UUID(execution_id))
            )
            execution = exec_result.scalar_one_or_none()
            if execution is None:
                return {"status": "error", "message": "Execution not found"}

            step_result = await session.execute(
                select(WorkflowStep).where(WorkflowStep.id == UUID(step_id))
            )
            step = step_result.scalar_one_or_none()
            if step is None:
                return {"status": "error", "message": "Step not found"}

            # Find the step log
            log_result = await session.execute(
                select(WorkflowStepLog).where(
                    WorkflowStepLog.execution_id == execution.id,
                    WorkflowStepLog.step_id == step.id,
                )
            )
            step_log = log_result.scalar_one_or_none()
            if step_log is None:
                step_log = WorkflowStepLog(
                    execution_id=execution.id,
                    step_id=step.id,
                    status=WorkflowExecutionStatus.RUNNING,
                    started_at=datetime.now(timezone.utc),
                )
                session.add(step_log)
                await session.flush()

            start_time = time.monotonic()
            step_log.status = WorkflowExecutionStatus.RUNNING
            step_log.started_at = datetime.now(timezone.utc)
            session.add(step_log)
            await session.flush()

            # Evaluate condition if present
            if step.condition:
                trigger_data = execution.trigger_data or {}
                from app.services.workflow_service import _evaluate_conditions
                if not _evaluate_conditions(step.condition, trigger_data):
                    step_log.status = WorkflowExecutionStatus.COMPLETED
                    step_log.completed_at = datetime.now(timezone.utc)
                    step_log.output_data = {"reason": "Condition not met", "skipped": True}
                    session.add(step_log)
                    # Advance to next step
                    await _advance_to_next(session, execution, step)
                    await session.commit()
                    return {"status": "skipped", "reason": "Condition not met"}

            # Execute the step based on its type and config
            try:
                output = await _execute_step_action(session, step, execution)
                step_log.status = WorkflowExecutionStatus.COMPLETED
                step_log.output_data = output
            except Exception as exc:
                step_log.status = WorkflowExecutionStatus.FAILED
                step_log.error_message = str(exc)

                if step.on_failure == "skip":
                    logger.warning("Step %s failed, skipping: %s", step.name, exc)
                else:
                    # Stop execution
                    execution.status = WorkflowExecutionStatus.FAILED
                    execution.error_message = f"Step '{step.name}' failed: {exc}"
                    execution.completed_at = datetime.now(timezone.utc)
                    session.add(execution)
                    session.add(step_log)
                    await session.commit()
                    return {"status": "failed", "error": str(exc)}

            step_log.completed_at = datetime.now(timezone.utc)
            session.add(step_log)

            # Advance to next step
            await _advance_to_next(session, execution, step)
            await session.commit()

            return {
                "status": step_log.status.value,
                "step": step.name,
            }

    try:
        return _run_async(_execute())
    except Exception as exc:
        logger.exception("Workflow step execution failed: step=%s exec=%s", step_id, execution_id)
        raise self.retry(exc=exc)


async def _execute_step_action(session, step, execution) -> dict:
    """Execute the actual action for a workflow step based on its config."""
    config = step.config or {}
    action_type = config.get("action_type", step.step_type.value if step.step_type else "noop")
    parameters = config.get("parameters", {})

    if action_type == "send_notification":
        from app.constants import ChannelType, NotificationStatus
        from app.models.communication import Notification
        notif = Notification(
            user_id=parameters.get("recipient_id"),
            channel=ChannelType(parameters.get("channel", "in_app")),
            title=parameters.get("subject", "Workflow Notification"),
            message=parameters.get("body", "A workflow step has been triggered."),
            status=NotificationStatus.PENDING,
        )
        session.add(notif)
        return {"action": "send_notification", "result": "queued"}

    elif action_type == "update_status":
        from uuid import UUID
        from app.constants import CaseStatus
        from app.models.case import Case
        case_id = parameters.get("case_id") or (execution.trigger_data or {}).get("case_id")
        new_status = parameters.get("status")
        if case_id and new_status:
            from sqlalchemy import select
            case_result = await session.execute(select(Case).where(Case.id == UUID(str(case_id))))
            case = case_result.scalar_one_or_none()
            if case:
                try:
                    case.status = CaseStatus(new_status)
                except ValueError:
                    pass
                session.add(case)
                return {"action": "update_status", "case_id": str(case_id), "new_status": new_status}
        return {"action": "update_status", "result": "no_op"}

    elif action_type == "create_case":
        return {"action": "create_case", "result": "placeholder_created"}

    elif action_type == "assign_task":
        return {"action": "assign_task", "result": "placeholder_assigned"}

    elif action_type == "schedule_appointment":
        return {"action": "schedule_appointment", "result": "placeholder_scheduled"}

    elif action_type == "check_eligibility":
        from app.services.ai_service import assess_eligibility
        intake_data = parameters.get("intake_data", execution.trigger_data or {})
        assessment = await assess_eligibility(intake_data)
        return {"action": "check_eligibility", "result": assessment}

    elif action_type == "request_approval":
        return {"action": "request_approval", "result": "approval_pending", "approver": parameters.get("approver_id")}

    elif action_type == "generate_document":
        return {"action": "generate_document", "result": "placeholder_generated"}

    else:
        logger.info("Executing generic step '%s' with action_type '%s'", step.name, action_type)
        return {"action": action_type, "result": "executed", "parameters": parameters}


async def _advance_to_next(session, execution, current_step):
    """Find and dispatch the next step in the workflow, or mark execution complete."""
    from sqlalchemy import select
    from app.constants import WorkflowExecutionStatus
    from app.models.workflow import WorkflowStep

    next_result = await session.execute(
        select(WorkflowStep)
        .where(
            WorkflowStep.workflow_id == current_step.workflow_id,
            WorkflowStep.step_order > current_step.step_order,
        )
        .order_by(WorkflowStep.step_order)
        .limit(1)
    )
    next_step = next_result.scalar_one_or_none()

    if next_step:
        execution.current_step = next_step.step_order
        session.add(execution)
        # Dispatch next step
        execute_workflow_step.delay(str(execution.id), str(next_step.id))
    else:
        # Workflow complete
        execution.status = WorkflowExecutionStatus.COMPLETED
        execution.completed_at = datetime.now(timezone.utc)
        session.add(execution)
        logger.info("Workflow execution %s completed", execution.id)
