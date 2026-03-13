"""Root API router that includes all v1 routers with prefixes and tags."""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    billing,
    cases,
    clients,
    communication,
    documents,
    intake,
    reporting,
    scheduling,
    tasks,
    wealth,
    workflows,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(clients.router, prefix="/clients", tags=["Clients"])
api_router.include_router(cases.router, prefix="/cases", tags=["Cases"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(intake.router, prefix="/intake", tags=["Intake"])
api_router.include_router(scheduling.router, prefix="/scheduling", tags=["Scheduling"])
api_router.include_router(communication.router, prefix="/communication", tags=["Communication"])
api_router.include_router(billing.router, prefix="/billing", tags=["Billing"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(wealth.router, prefix="/wealth", tags=["Wealth Building"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])
api_router.include_router(reporting.router, prefix="/reporting", tags=["Reporting"])
