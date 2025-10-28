from typing import Sequence, Optional
from sqlalchemy import or_
from sqlalchemy.future import select

from db import AsyncSession
from models.user import UserModel
from models.role import RoleModel
from models.permission import PermissionModel
from common.exception import ApiException
from common.utils import get_db_model_fields
from schemas.role import RoleCreateSchema, RoleUpdateSchema
from common.pagination import PaginationQuerySchema, PaginationSchema, pagination

import services.permission as PermissionServer


async def delete_by_id(id: int, session: AsyncSession):
    obj = await get_obj_by_query({'id': id}, session)
    if not obj:
        raise ApiException('角色不存在')
    
    # 逻辑删除
    setattr(obj, 'is_delete', True)
    await session.commit()
    await session.refresh(obj)


async def dispatch_permission(id: int, permission_ids: list[int], session: AsyncSession) -> RoleModel:
    obj = await get_obj_by_query({'id': id}, session)
    if not obj:
        raise ApiException('角色不存在')
    
    permission_objs = await PermissionServer.all_permission_by_ids(permission_ids, session)
    obj.permissions = permission_objs
    await session.commit()
    await session.refresh(obj)
    return obj


async def change_status(id: int, enable: bool, session: AsyncSession) -> RoleModel:
    obj = await get_obj_by_query({'id': id}, session)
    if not obj:
        raise ApiException('角色不存在')

    setattr(obj, 'enable', enable)
    await session.commit()
    await session.refresh(obj)
    return obj


async def update_by_id(id: int, data: RoleUpdateSchema, session: AsyncSession) -> RoleModel:
    obj = await get_obj_by_query({'id': id}, session)
    if not obj:
        raise ApiException('角色不存在')
    
    # 角色编码和名称唯一
    if not await check_role_exist(data.name, data.code, session):
        raise ApiException('角色已存在，请换个名称或者编码')

    for k, v in data.model_dump().items():
        if v is None:
            continue
        setattr(obj, k, v)
    await session.commit()
    await session.refresh(obj)
    return obj


async def check_role_exist(name: str, code: str, session: AsyncSession) -> bool:
    result = await session.execute(select(RoleModel)
        .filter(or_(RoleModel.name == name, RoleModel.code == code))
        .filter(RoleModel.is_delete == False)
    )
    obj = result.scalars().first()
    return obj is not None


async def get_obj_by_query(query: dict, session: AsyncSession) -> RoleModel:
    # 过滤掉不存在的参数
    fields = get_db_model_fields(RoleModel)
    query = {k: v for k, v in query.items() if k in fields}

    result = await session.execute(select(RoleModel).filter_by(**query).filter(RoleModel.is_delete==False))
    obj = result.scalars().first()
    return obj


async def create_obj(data: RoleCreateSchema, session: AsyncSession) -> RoleModel:
    # 这里ID为-1的原因:排除id的影响，因为如果存在不可能有任何id和-1相等（正常情况下）
    if await check_role_exist(data.name, data.code, session):
        raise ApiException('该角色已存在')
    
    obj = RoleModel(**data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def all_role_list_by_enable(keyword: Optional[str], session: AsyncSession) -> Sequence[RoleModel]:
    query = {'is_delete': False, 'enable': True}
    stmt = select(RoleModel).filter_by(**query)
    if keyword is not None:
        keyword = f'%{keyword}%'
        stmt = stmt.filter(or_(RoleModel.name.like(keyword), RoleModel.code.like(keyword)))
        
    result = await session.execute(stmt)
    return result.scalars().all()


async def pagelist(schema: PaginationQuerySchema, session: AsyncSession) -> tuple[PaginationSchema, Sequence[RoleModel]]:
    return await pagination(RoleModel, schema, session)
