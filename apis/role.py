from typing import Optional
import services.role as RoleService
from fastapi import APIRouter, Depends

from common.log import logger
from config import AUTH_CONFIG
from db import AsyncSession, async_session
from common.auth import RoutePermission
from common.response import CommonResponse
from common.exception import ApiException
from common.depends import get_query_params
from common.pagination import PaginationQuerySchema
from common.permission_enum import MenuEnum, InterfaceEnum, ButtionEnum

from models.user import UserModel
from models.permission import PermissionEnum
from schemas.permission import PermissionSchema
from schemas.role import RoleSchema, RoleCreateSchema, RoleUpdateSchema, RoleUpdatePermissionSchema


router = APIRouter()

@router.put('/{id}', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.ROLE_MANAGE],
        buttion_list=[ButtionEnum.ROLE_EDIT]
).to_openapi_extra())
async def update(id: int, data: RoleUpdateSchema, session: AsyncSession = Depends(async_session)) -> CommonResponse:
    logger.info(f'id: {id}, data: {data.model_dump()}')
    # 如果需要修改的角色信息不是超级管理员，随便修改
    role = await RoleService.get_obj_by_query({'id': id, 'code': AUTH_CONFIG.manage.super_admin_code}, session)
    if not role:
        obj = await RoleService.update_by_id(id, data, session)
        return CommonResponse.success(data=RoleSchema.model_validate(obj).model_dump())
    # 否则不支持修改信息
    raise ApiException('该角色不支持修改')


@router.put('/dispatch-permission/{id}', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.ROLE_MANAGE],
        buttion_list=[ButtionEnum.ROLE_EDIT]
).to_openapi_extra())
async def update_permission(id: int, data: RoleUpdatePermissionSchema, session: AsyncSession = Depends(async_session)) -> CommonResponse:
    logger.info(f'id: {id}, data: {data.model_dump()}')
    # 如果需要修改的角色信息不是超级管理员，随便修改
    role = await RoleService.get_obj_by_query({'id': id, 'code': AUTH_CONFIG.manage.super_admin_code}, session)
    if not role:
        obj = await RoleService.dispatch_permission(id, data.permission_ids, session)
        return CommonResponse.success(data=RoleSchema.model_validate(obj).model_dump())
    # 否则不支持修改信息
    raise ApiException('该角色不支持修改')


@router.delete('/{id}', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.ROLE_MANAGE],
        buttion_list=[ButtionEnum.ROLE_DEL]
).to_openapi_extra())
async def delete(id: int, session: AsyncSession = Depends(async_session)) -> CommonResponse:
    logger.info(f'id: {id}')
    await RoleService.delete_by_id(id, session)
    return CommonResponse.success(data=True)


@router.post('/', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.ROLE_MANAGE],
        buttion_list=[ButtionEnum.ROLE_ADD]
).to_openapi_extra())
async def post(data: RoleCreateSchema, session: AsyncSession = Depends(async_session)) -> CommonResponse:
    logger.info(f'data: {data.model_dump()}')
    obj = await RoleService.create_obj(data, session)
    return CommonResponse.success(data=RoleSchema.model_validate(obj).model_dump())


@router.get('/all', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.ROLE_MANAGE]
).to_openapi_extra())
async def all_role_list(keyword: Optional[str] = None, session: AsyncSession = Depends(async_session)):
    obj_list = await RoleService.all_role_list_by_enable(keyword, session)
    return CommonResponse.success(data=[RoleSchema.model_validate(obj).model_dump() for obj in obj_list])


@router.get('/list', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.ROLE_MANAGE]
).to_openapi_extra())
async def pagelist(data: PaginationQuerySchema = Depends(get_query_params), session: AsyncSession = Depends(async_session)):
    pagination, obj_list = await RoleService.pagelist(data, session)
    return CommonResponse.success(data={
        'records': [RoleSchema.model_validate(obj).model_dump() for obj in obj_list],
        **pagination.model_dump()
    })


@router.get('/{id}', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.ROLE_MANAGE],
        buttion_list=[ButtionEnum.ROLE_EDIT]
).to_openapi_extra())
async def get_by_id(id: int, session: AsyncSession = Depends(async_session)) -> CommonResponse:
    logger.info(f'id: {id}')
    role = await RoleService.get_obj_by_query({'id': id}, session)
    role_dict = RoleSchema.model_validate(role).model_dump()
    permission_dict = {'menu': [], 'interface': [], 'button': []}
    for obj in role.permissions:
        obj_dict = PermissionSchema.model_validate(obj).model_dump()
        if getattr(obj, 'type') == PermissionEnum.MENU:
            permission_dict['menu'].append(obj_dict)
        elif getattr(obj, 'type') == PermissionEnum.INTERFACE:
            permission_dict['interface'].append(obj_dict)
        elif getattr(obj, 'type') == PermissionEnum.BUTTON:
            permission_dict['button'].append(obj_dict)
    role_dict['permission'] = permission_dict
    return CommonResponse.success(data=role_dict)
