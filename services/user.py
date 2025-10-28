from typing import Sequence, Optional
from sqlalchemy.future import select

from db import AsyncSession
from models.user import UserModel
from models.role import RoleModel
from models.permission import PermissionModel
from models.role_permission import RolePermissionModel

from common.exception import ApiException
from common.utils import get_db_model_fields
from common.pagination import PaginationQuerySchema, PaginationSchema, pagination

import services.role as RoleService
from schemas.user import UserCreateSchema, UserUpdateSchema


async def delete_by_id(id: int, session: AsyncSession):
    obj = await get_obj_by_query({'id': id}, session)
    if not obj:
        raise ApiException('用户不存在')
    
    # 逻辑删除
    setattr(obj, 'is_delete', True)
    await session.commit()
    await session.refresh(obj)


async def change_status(id: int, enable: bool, session: AsyncSession) -> UserModel:
    obj = await get_obj_by_query({'id': id}, session)
    if not obj:
        raise ApiException('用户不存在')

    setattr(obj, 'enable', enable)
    await session.commit()
    await session.refresh(obj)
    return obj


async def update_by_id(id: int, data: UserUpdateSchema, session: AsyncSession) -> UserModel:
    obj = await get_obj_by_query({'id': id}, session)
    if not obj:
        raise ApiException('用户不存在')
    
    # 用户名唯一，故如果用户名需要修改，需要先判定用户名是否可用
    if not await check_name(id, data.name, session):
        raise ApiException('用户名已存在，请换个用户名')

    for k, v in data.model_dump().items():
        if v is None:
            continue
        setattr(obj, k, v)
    await session.commit()
    await session.refresh(obj)
    return obj


async def check_name(id: int, name: Optional[str], session: AsyncSession) -> bool:
    if not name:
        return True
    
    obj = await get_obj_by_query({'name': name}, session)
    return obj is None or getattr(obj, 'id') == id


async def get_obj_by_query(query: dict, session: AsyncSession) -> UserModel:
    ''' 基于查询参数获取用户信息 '''
    # 过滤掉不存在的参数
    fields = get_db_model_fields(UserModel)
    query = {k: v for k, v in query.items() if k in fields}

    result = await session.execute(select(UserModel).filter_by(**query).filter(UserModel.is_delete==False))
    obj = result.scalars().first()
    return obj


async def create_user(data: UserCreateSchema, session: AsyncSession) -> UserModel:
    # 校验该用户名是否已存在
    result = await session.execute(
        select(UserModel).filter(UserModel.is_delete==False, UserModel.name==data.name)
    )
    if result.scalars().first():
        raise ApiException('该用户已存在')
    
    # 创建用户
    user = UserModel(**data.model_dump())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def user_dispatch_role(id: int, role_id: int, session: AsyncSession) -> UserModel:
    user = await get_obj_by_query({'id': id}, session)
    if user is None:
        raise ApiException('该用户不存在！')
    
    role = await RoleService.get_obj_by_query({'id': role_id, 'enable': True}, session)
    if role is None:
        raise ApiException('角色不存在')

    user.role = role
    await session.commit()
    await session.refresh(user)
    return user


async def pagelist(schema: PaginationQuerySchema, session: AsyncSession) -> tuple[PaginationSchema, Sequence[UserModel]]:
    return await pagination(UserModel, schema, session)
