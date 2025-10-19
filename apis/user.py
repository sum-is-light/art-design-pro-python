from fastapi import APIRouter, Depends

from common.auth import RoutePermission
from common.response import CommonResponse
from common.permission_enum import MenuEnum, InterfaceEnum, ButtionEnum

from db import AsyncSession, async_session
from common.log import logger
from common.response import CommonResponse
from schemas.user import UserCreateSchema, UserSchema
import services.user as UserService
from common.pagination import PaginationQuerySchema
from common.depends import get_query_params

router = APIRouter()

@router.get('/list', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.USER_MANAGE]
).to_openapi_extra())
async def pagelist(data: PaginationQuerySchema = Depends(get_query_params), session: AsyncSession = Depends(async_session)):
    pagination, obj_list = await UserService.pagelist(data, session)
    return CommonResponse.success(data={
        'records': [UserSchema.model_validate(obj).model_dump() for obj in obj_list],
        **pagination.model_dump()
    })


@router.post('/', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.USER_MANAGE],
        interface_list=[InterfaceEnum.USER_POST],
        buttion_list=[ButtionEnum.USER_ADD]
).to_openapi_extra())
async def create_user(data: UserCreateSchema, session: AsyncSession = Depends(async_session)) -> CommonResponse:
    logger.info(f'data: {data.model_dump()}')
    return await UserService.create_user(data, session)
