from dataclasses import dataclass
from typing import Any, Generic, Sequence, TypeVar

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


@dataclass
class PaginationParams:
    page: int = 1
    size: int = 20

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(20, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.size = size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int

    model_config = {"from_attributes": True}


async def paginate(
    session: AsyncSession,
    query: Select,
    params: PaginationParams,
    response_model: type[Any] | None = None,
) -> PaginatedResponse:
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    paginated_query = query.offset(params.offset).limit(params.size)
    result = await session.execute(paginated_query)
    rows = result.scalars().all()

    items: Sequence[Any]
    if response_model is not None:
        items = [response_model.model_validate(row) for row in rows]
    else:
        items = list(rows)

    pages = max(1, (total + params.size - 1) // params.size)

    return PaginatedResponse(
        items=items,
        total=total,
        page=params.page,
        size=params.size,
        pages=pages,
    )
