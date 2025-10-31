import services.user as UserService
from fastapi import APIRouter, Depends

from common.log import logger
from config import AUTH_CONFIG
from db import AsyncSession, async_session
from common.response import CommonResponse
from common.pagination import PaginationQuerySchema
from common.auth import RoutePermission, generate_token
from common.depends import get_query_params, check_permission
from common.permission_enum import MenuEnum, InterfaceEnum, ButtionEnum

from models.role import RoleModel
from models.user import UserModel

from schemas.role import RoleSchema
from schemas.user import (
    UserCreateSchema, UserSchema, UserLoginSchema, UserUpdateSchema,
    UserChangeStatusSchema, UserDispatchRoleSchema
)


router = APIRouter()


@router.put('/change_status/{uid}', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.USER_MANAGE],
        interface_list=[InterfaceEnum.USER_ENABLE],
        buttion_list=[ButtionEnum.USER_EDIT]
).to_openapi_extra())
async def change_status(uid: int, data: UserChangeStatusSchema, session: AsyncSession = Depends(async_session)) -> CommonResponse:
    logger.info(f'userId: {uid}, status: {data.enable}')
    await UserService.change_status(uid, data.enable, session)
    return CommonResponse.success(data=True)


@router.post('/dispatch/{uid}', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.USER_MANAGE],
        buttion_list=[ButtionEnum.USER_DISPATCH_ROLE]
).to_openapi_extra())
async def user_dispatch_role(uid: int, data: UserDispatchRoleSchema, session: AsyncSession = Depends(async_session)) -> CommonResponse:
    logger.info(f'userId: {uid}, data: {data.model_dump()}')
    await UserService.user_dispatch_role(uid, data.rid, session)
    return CommonResponse.success(data=True)


@router.put('/{uid}', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.USER_MANAGE],
        interface_list=[InterfaceEnum.USER_PUT],
        buttion_list=[ButtionEnum.USER_EDIT]
).to_openapi_extra())
async def update(uid: int, data: UserUpdateSchema, session: AsyncSession = Depends(async_session)) -> CommonResponse:
    logger.info(f'userId: {uid}, data: {data.model_dump()}')
    user = await UserService.update_by_id(uid, data, session)
    return CommonResponse.success(data=UserSchema.model_validate(user).model_dump())


@router.delete('/{uid}', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.USER_MANAGE],
        interface_list=[InterfaceEnum.USER_DEL],
        buttion_list=[ButtionEnum.USER_DEL]
).to_openapi_extra())
async def delete(uid: int, session: AsyncSession = Depends(async_session)) -> CommonResponse:
    logger.info(f'userId: {uid}')
    await UserService.delete_by_id(uid, session)
    return CommonResponse.success(data=True)


@router.post('/login')
async def login(data: UserLoginSchema, session: AsyncSession = Depends(async_session)):
    ''' 用户登录接口 '''
    obj = await UserService.get_obj_by_query({ 'name': data.name }, session)
    if not obj:
        return CommonResponse.fail(msg='用户不存在')
    
    if not obj.check_pwd(data.password):
        return CommonResponse.fail(msg='用户名或密码错误')
    user_dict = UserSchema.model_validate(obj).model_dump(include={'id', 'name'})
    # 登录成功生成token并返回
    return CommonResponse.success(data={
        'token': generate_token(user_dict, AUTH_CONFIG.jwt.secret_key, AUTH_CONFIG.jwt.expire_minute, AUTH_CONFIG.jwt.algorithm)
    })


@router.get('/info', openapi_extra=RoutePermission(
        interface_list=[InterfaceEnum.USER_GET]
).to_openapi_extra())
async def info(user: UserService.UserModel = Depends(check_permission), session: AsyncSession = Depends(async_session)):
    ''' 获取用户信息接口 '''
    user_dict = UserSchema.model_validate(user).model_dump()
    role: RoleModel = user.role
    if role != None:
        # 这里的roles其实是角色菜单权限列表
        user_dict['roles'] = role.get_permission_codes('menu')
        user_dict['buttons'] = role.get_permission_codes('button')
    return CommonResponse.success(data=user_dict)


@router.get('/list', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.USER_MANAGE]
).to_openapi_extra())
async def pagelist(data: PaginationQuerySchema = Depends(get_query_params), session: AsyncSession = Depends(async_session)):
    pagination, obj_list = await UserService.pagelist(data, session)
    return CommonResponse.success(data={
        'records': [UserSchema.model_validate(obj).model_dump() for obj in obj_list],
        **pagination.model_dump()
    })


@router.get('/{uid}', openapi_extra=RoutePermission(
        interface_list=[InterfaceEnum.USER_GET]
).to_openapi_extra())
async def get_info_by_id(uid: int, session: AsyncSession = Depends(async_session)):
    ''' 获取用户信息接口 '''
    user = await UserService.get_obj_by_query({'id': uid}, session)
    user_dict = UserSchema.model_validate(user).model_dump()
    user_dict['role'] = RoleSchema.model_validate(user.role).model_dump() if user.role else {}
    return CommonResponse.success(data=user_dict)


@router.post('/', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.USER_MANAGE],
        interface_list=[InterfaceEnum.USER_POST],
        buttion_list=[ButtionEnum.USER_ADD]
).to_openapi_extra())
async def post(data: UserCreateSchema, session: AsyncSession = Depends(async_session)) -> CommonResponse:
    logger.info(f'data: {data.model_dump()}')
    user = await UserService.create_user(data, session)
    return CommonResponse.success(data=UserSchema.model_validate(user).model_dump())
