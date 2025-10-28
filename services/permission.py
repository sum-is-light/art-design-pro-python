from typing import Sequence, Optional

from sqlalchemy import or_
from sqlalchemy.future import select

from db import AsyncSession
from models.user import UserModel
from models.role import RoleModel
from models.permission import PermissionModel
from common.exception import ApiException
from common.utils import get_db_model_fields
from schemas.permission import PermissionCreateSchema, PermissionUpdateSchema
from common.pagination import PaginationQuerySchema, PaginationSchema, pagination


async def delete_by_id(id: int, session: AsyncSession):
    obj = await get_obj_by_query({'id': id}, session)
    if not obj:
        raise ApiException('权限不存在')
    
    # 逻辑删除
    setattr(obj, 'is_delete', True)
    await session.commit()
    await session.refresh(obj)


async def change_status(id: int, enable: bool, session: AsyncSession) -> PermissionModel:
    obj = await get_obj_by_query({'id': id}, session)
    if not obj:
        raise ApiException('权限不存在')

    setattr(obj, 'enable', enable)
    await session.commit()
    await session.refresh(obj)
    return obj


async def update_by_id(id: int, data: PermissionUpdateSchema, session: AsyncSession) -> PermissionModel:
    obj = await get_obj_by_query({'id': id}, session)
    if not obj:
        raise ApiException('权限不存在')
    
    for k, v in data.model_dump().items():
        if v is None:
            continue
        setattr(obj, k, v)
    await session.commit()
    await session.refresh(obj)
    return obj


async def check_permission_exist(name: str, code: str, session: AsyncSession) -> bool:
    result = await session.execute(select(PermissionModel)
        .filter(or_(PermissionModel.name == name, PermissionModel.code == code))
        .filter(PermissionModel.is_delete == False)
    )
    obj = result.scalars().first()
    return obj is not None


async def get_obj_by_query(query: dict, session: AsyncSession) -> PermissionModel:
    # 过滤掉不存在的参数
    fields = get_db_model_fields(PermissionModel)
    query = {k: v for k, v in query.items() if k in fields}

    result = await session.execute(select(PermissionModel).filter_by(**query).filter(PermissionModel.is_delete==False))
    obj = result.scalars().first()
    return obj


async def create_obj(data: PermissionCreateSchema, session: AsyncSession) -> PermissionModel:
    if await check_permission_exist(data.name, data.code, session):
        raise ApiException('该权限已存在')
    
    obj = PermissionModel(**data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def all_permission_list_by_enable(session: AsyncSession, keyword: Optional[str] = None) -> Sequence[PermissionModel]:
    query = {'is_delete': False, 'enable': True}
    stmt = select(PermissionModel).filter_by(**query)
    if keyword is not None:
        keyword = f'%{keyword}%'
        stmt = stmt.filter(or_(PermissionModel.name.like(keyword), PermissionModel.code.like(keyword)))
        
    result = await session.execute(stmt)
    return result.scalars().all()


async def all_permission_by_ids(ids: list[int], session: AsyncSession) -> Sequence[PermissionModel]:
    query = {'is_delete': False, 'enable': True}
    stmt = select(PermissionModel).filter_by(**query).filter(PermissionModel.id.in_(ids))
    result = await session.execute(stmt)
    return result.scalars().all()


async def pagelist(schema: PaginationQuerySchema, session: AsyncSession) -> tuple[PaginationSchema, Sequence[PermissionModel]]:
    return await pagination(PermissionModel, schema, session)
