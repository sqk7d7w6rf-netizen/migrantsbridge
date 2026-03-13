from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, detail: str, status_code: int = 500):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class NotFoundError(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail=detail, status_code=404)


class UnauthorizedError(AppException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(detail=detail, status_code=401)


class ForbiddenError(AppException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(detail=detail, status_code=403)


class ValidationError(AppException):
    def __init__(self, detail: str = "Validation error"):
        super().__init__(detail=detail, status_code=422)


class ConflictError(AppException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(detail=detail, status_code=409)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "type": type(exc).__name__,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "InternalServerError",
        },
    )
