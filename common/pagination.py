from sqlalchemy import func
from sqlalchemy.future import select
from typing import Sequence, Any
from pydantic import BaseModel, Field

from common.log import logger
from common.utils import get_db_model_fields
from db import AsyncSession, DBBaseModel, Column


class PaginationQuerySchema(BaseModel):
    page: int = Field(default=1, description='页码')
    size: int = Field(default=10, description='每一页的数量')

    query: dict[str, Any] = Field(default=dict(), description='查询参数')


class PaginationSchema(BaseModel):
    page: int = Field(default=1, description='页码')
    size: int = Field(default=10, description='每一页的数量')
    has_prev: bool = Field(description='是否有上一页')
    has_next: bool = Field(description='是否有下一页')
    total: int = Field(description='数据总数')


async def pagination(
    model: type[DBBaseModel], pagination_query: PaginationQuerySchema, session: AsyncSession
) -> tuple[PaginationSchema, Sequence[DBBaseModel]]:
    fields = get_db_model_fields(model)
    query = {k: v for k, v in pagination_query.query.items() if k in fields}
    logger.info(f'pagination_query: {pagination_query.model_dump()}, query: {query}')
    # 如果是字符串则使用like，其他使用等于
    filter_colums = []
    for k, v in query.items():
        # is_delete这个字段不支持外部控制
        if k == 'is_delete':
            continue
        column: Column = getattr(model, k)
        filter_colums.append(column.like(f'%{v}%') if isinstance(v, str) else column == v)
    
    # 执行查询并将结果返回
    pagination_stmt = select(func.count()).select_from(model).filter(*filter_colums).filter_by(is_delete=False)
    result = await session.execute(pagination_stmt)
    total = result.scalar_one_or_none() or 0

    result = await session.execute(
        select(model).filter(*filter_colums).filter_by(is_delete=False).offset((pagination_query.page - 1) * pagination_query.size).limit(pagination_query.size)
    )
    has_prev = pagination_query.page != 1
    has_next = (pagination_query.page * pagination_query.size) < total
    return PaginationSchema(
        total=total, has_prev=has_prev, has_next=has_next,
        **pagination_query.model_dump()
    ), result.scalars().all()
