from sqlalchemy import func
from typing import Sequence
from sqlalchemy.future import select
from pydantic import BaseModel, Field

from common.log import logger
from db import AsyncSession, DBBaseModel


class PaginationQuerySchema(BaseModel):
    page: int = Field(default=1, description='页码')
    size: int = Field(default=10, description='每一页的数量')


class PaginationSchema(BaseModel):
    page: int = Field(default=1, description='页码')
    size: int = Field(default=10, description='每一页的数量')
    has_prev: bool = Field(description='是否有上一页')
    has_next: bool = Field(description='是否有下一页')
    total: int = Field(description='数据总数')


async def pagination(
    model: type[DBBaseModel], pagination_query: PaginationQuerySchema, query: dict, session: AsyncSession
) -> tuple[PaginationSchema, Sequence[DBBaseModel]]:
    logger.info(f'pagination_query: {pagination_query.model_dump()}, query: {query}')
    if 'is_delete' not in query:
        query['is_delete'] = False
    elif query['is_delete'] is None:
        query.pop('is_delete')
    
    pagination_stmt = select(func.count()).select_from(model).filter_by(**query)
    result = await session.execute(pagination_stmt)
    total = result.scalar_one_or_none() or 0

    result = await session.execute(
        select(model).filter_by(**query).offset((pagination_query.page - 1) * pagination_query.size).limit(pagination_query.size)
    )
    has_prev = pagination_query.page != 1
    has_next = (pagination_query.page * pagination_query.size) < total
    return PaginationSchema(
        total=total, has_prev=has_prev, has_next=has_next,
        **pagination_query.model_dump()
    ), result.scalars().all()
