from typing import Optional
from fastapi import APIRouter, Depends
import services.permission as PermissionService

from common.log import logger
from db import AsyncSession, async_session
from common.auth import RoutePermission
from common.response import CommonResponse
from common.depends import get_query_params
from common.pagination import PaginationQuerySchema
from common.permission_enum import MenuEnum, InterfaceEnum, ButtonEnum

from models.enums import PermissionEnum
from schemas.permission import PermissionSchema, PermissionCreateSchema, PermissionUpdateSchema


router = APIRouter()

@router.put('/{id}', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.PERMISSION_MANAGE],
        button_list=[ButtonEnum.PERMISSION_EDIT]
).to_openapi_extra())
async def update(id: int, data: PermissionUpdateSchema, session: AsyncSession = Depends(async_session)) -> CommonResponse:
    logger.info(f'id: {id}, data: {data.model_dump()}')
    obj = await PermissionService.update_by_id(id, data, session)
    return CommonResponse.success(data=PermissionSchema.model_validate(obj).model_dump())


@router.delete('/{id}', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.PERMISSION_MANAGE],
        button_list=[ButtonEnum.PERMISSION_DEL]
).to_openapi_extra())
async def delete(id: int, session: AsyncSession = Depends(async_session)) -> CommonResponse:
    logger.info(f'id: {id}')
    await PermissionService.delete_by_id(id, session)
    return CommonResponse.success(data=True)


@router.post('/', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.PERMISSION_MANAGE],
        button_list=[ButtonEnum.PERMISSION_ADD]
).to_openapi_extra())
async def post(data: PermissionCreateSchema, session: AsyncSession = Depends(async_session)) -> CommonResponse:
    logger.info(f'data: {data.model_dump()}')
    obj = await PermissionService.create_obj(data, session)
    return CommonResponse.success(data=PermissionSchema.model_validate(obj).model_dump())


@router.get('/all', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.PERMISSION_MANAGE]
).to_openapi_extra())
async def all_permission_list(keyword: Optional[str] = None, session: AsyncSession = Depends(async_session)):
    obj_list = await PermissionService.all_permission_list_by_enable(session, keyword)
    return CommonResponse.success(data=[PermissionSchema.model_validate(obj).model_dump() for obj in obj_list])


@router.get('/group-all', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.PERMISSION_MANAGE]
).to_openapi_extra())
async def all_permission_list_by_type(keyword: Optional[str] = None, session: AsyncSession = Depends(async_session)):
    obj_list = await PermissionService.all_permission_list_by_enable(session, keyword)
    data_dict = {'menu': [], 'interface': [], 'button': []}
    for obj in obj_list:
        obj_dict = PermissionSchema.model_validate(obj).model_dump()
        if getattr(obj, 'type') == PermissionEnum.MENU:
            data_dict['menu'].append(obj_dict)
        elif getattr(obj, 'type') == PermissionEnum.INTERFACE:
            data_dict['interface'].append(obj_dict)
        elif getattr(obj, 'type') == PermissionEnum.BUTTON:
            data_dict['button'].append(obj_dict)
    return CommonResponse.success(data=data_dict)


@router.get('/list', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.PERMISSION_MANAGE]
).to_openapi_extra())
async def pagelist(data: PaginationQuerySchema = Depends(get_query_params), session: AsyncSession = Depends(async_session)):
    pagination, obj_list = await PermissionService.pagelist(data, session)
    return CommonResponse.success(data={
        'records': [PermissionSchema.model_validate(obj).model_dump() for obj in obj_list],
        **pagination.model_dump()
    })
