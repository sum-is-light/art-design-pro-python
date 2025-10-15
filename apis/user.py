from fastapi import APIRouter, Depends

from common.auth import RoutePermission
from common.response import CommonResponse
from common.permission_enum import MenuEnum, InterfaceEnum, ButtionEnum

from db import AsyncSession, async_session
import services.user as UserService
from common.log import logger
from common.response import CommonResponse
from schemas.user import UserCreateSchema

router = APIRouter()

@router.get('/', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.USER_MANAGE],
        interface_list=[InterfaceEnum.USER_GET]
).to_openapi_extra())
async def get():
    return CommonResponse.success('没问题', {'temp': UserService.get_list()})


@router.post('/', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.USER_MANAGE],
        interface_list=[InterfaceEnum.USER_POST],
        buttion_list=[ButtionEnum.USER_ADD]
).to_openapi_extra())
async def create_user(data: UserCreateSchema, session: AsyncSession = Depends(async_session)) -> CommonResponse:
    logger.info(f'data: {data.model_dump()}')
    return await UserService.create_user(data, session)
