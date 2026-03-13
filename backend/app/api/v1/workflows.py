"""Workflow engine API routes: CRUD, AI generation, execution, routing rules."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.pagination import PaginatedResponse, PaginationParams
from app.core.security import get_current_user
from app.schemas.common import SuccessResponse
from app.schemas.workflow import (
    RoutingRuleCreate,
    RoutingRuleRead,
    StepLogRead,
    WorkflowCreate,
    WorkflowExecutionRead,
    WorkflowGenerateRequest,
    WorkflowRead,
    WorkflowUpdate,
)
from app.services import ai_service, workflow_service

router = APIRouter()


# --- AI Generation ---

@router.post("/generate", response_model=WorkflowRead, status_code=201)
async def generate_workflow(
    payload: WorkflowGenerateRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Use AI to generate a workflow from a natural language description."""
    generated = await ai_service.generate_workflow(
        payload.natural_language_description, payload.context
    )

    # Convert AI output to a WorkflowCreate schema
    from app.schemas.workflow import WorkflowStepCreate, StepType, TriggerType

    steps = []
    for step_data in generated.get("steps", []):
        steps.append(WorkflowStepCreate(
            name=step_data.get("name", "Unnamed Step"),
            step_type=StepType(step_data.get("step_type", "action")),
            order=step_data.get("order", 0),
            config=step_data.get("config", {}),
            condition=step_data.get("condition"),
            timeout_seconds=step_data.get("timeout_seconds"),
            retry_count=step_data.get("retry_count", 0),
            on_failure=step_data.get("on_failure", "stop"),
        ))

    create_payload = WorkflowCreate(
        name=generated.get("name", "AI-Generated Workflow"),
        description=generated.get("description", payload.natural_language_description),
        trigger_type=TriggerType(generated.get("trigger_type", "manual")),
        trigger_config=generated.get("trigger_config", {}),
        steps=steps,
    )

    return await workflow_service.create_workflow(session, create_payload, current_user.id)


# --- Workflow CRUD ---

@router.post("", response_model=WorkflowRead, status_code=201)
async def create_workflow(
    payload: WorkflowCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Create a new workflow."""
    return await workflow_service.create_workflow(session, payload, current_user.id)


@router.get("", response_model=PaginatedResponse[WorkflowRead])
async def list_workflows(
    pagination: PaginationParams = Depends(),
    status: str | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """List workflows with optional status filter."""
    return await workflow_service.list_workflows(session, pagination, status)


@router.get("/{workflow_id}", response_model=WorkflowRead)
async def get_workflow(
    workflow_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get a workflow by ID."""
    return await workflow_service.get_workflow(session, workflow_id)


@router.put("/{workflow_id}", response_model=WorkflowRead)
async def update_workflow(
    workflow_id: UUID,
    payload: WorkflowUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Update a workflow."""
    return await workflow_service.update_workflow(session, workflow_id, payload)


@router.delete("/{workflow_id}", response_model=SuccessResponse)
async def delete_workflow(
    workflow_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Soft-delete a workflow."""
    await workflow_service.delete_workflow(session, workflow_id)
    return SuccessResponse(message="Workflow deleted successfully")


# --- Execution ---

@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionRead, status_code=201)
async def execute_workflow(
    workflow_id: UUID,
    trigger_data: dict[str, Any] | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Start executing a workflow."""
    return await workflow_service.execute_workflow(session, workflow_id, trigger_data)


@router.get("/executions", response_model=PaginatedResponse[WorkflowExecutionRead])
async def list_executions(
    pagination: PaginationParams = Depends(),
    workflow_id: UUID | None = None,
    status: str | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """List workflow executions."""
    return await workflow_service.list_executions(session, pagination, workflow_id, status)


@router.get("/executions/{execution_id}", response_model=WorkflowExecutionRead)
async def get_execution(
    execution_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get a workflow execution by ID."""
    return await workflow_service.get_execution(session, execution_id)


@router.get("/executions/{execution_id}/logs", response_model=list[StepLogRead])
async def get_step_logs(
    execution_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get step execution logs for a workflow execution."""
    return await workflow_service.get_step_logs(session, execution_id)


# --- Routing Rules ---

@router.post("/routing-rules", response_model=RoutingRuleRead, status_code=201)
async def create_routing_rule(
    payload: RoutingRuleCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Create a routing rule."""
    return await workflow_service.create_routing_rule(session, payload)


@router.get("/routing-rules", response_model=PaginatedResponse[RoutingRuleRead])
async def list_routing_rules(
    pagination: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """List routing rules."""
    return await workflow_service.list_routing_rules(session, pagination)
