import os
from uuid import uuid4
from fastapi import APIRouter, Depends, File, UploadFile

import services.user as UserService
from db import AsyncSession, async_session
from config import AUTH_CONFIG, ENV_CONFIG, SOURCE_CONFIG

from common.log import logger
from common.response import CommonResponse
from common.pagination import PaginationQuerySchema
from common.auth import RoutePermission, generate_token
from common.depends import get_query_params, check_permission
from common.permission_enum import MenuEnum, InterfaceEnum, ButtonEnum

from models.role import RoleModel
from models.user import UserModel

from schemas.role import RoleSchema
from schemas.user import (
    UserCreateSchema, UserSchema, UserLoginSchema, UserUpdateSchema,
    UserChangeStatusSchema, UserDispatchRoleSchema, UserChangePasswordSchema
)


router = APIRouter()


@router.put('/change_status/{uid}', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.USER_MANAGE],
        interface_list=[InterfaceEnum.USER_ENABLE],
        button_list=[ButtonEnum.USER_EDIT]
).to_openapi_extra())
async def change_status(uid: int, data: UserChangeStatusSchema, session: AsyncSession = Depends(async_session)) -> CommonResponse:
    logger.info(f'userId: {uid}, status: {data.enable}')
    await UserService.change_status(uid, data.enable, session)
    return CommonResponse.success(data=True)


@router.post('/update', openapi_extra=RoutePermission(
        interface_list=[InterfaceEnum.USER_SELF_EDIT]
).to_openapi_extra())
async def update_self(data: UserUpdateSchema, user: UserService.UserModel = Depends(check_permission), session: AsyncSession = Depends(async_session)):
    ''' 更新用户自己的信息接口 '''
    user = await UserService.update_by_id(getattr(user, 'id'), data, session)
    user_dict = UserSchema.model_validate(user).model_dump()
    return CommonResponse.success(data=user_dict)


@router.post('/upload-avatar', openapi_extra=RoutePermission(
        interface_list=[InterfaceEnum.USER_SELF_EDIT]
).to_openapi_extra())
async def upload_avatar(avatar_file: UploadFile = File()):
    ''' 上传用户头像数据 '''
    # 获取需要保存的文件路径
    save_dir = os.path.join(ENV_CONFIG.source_dir, SOURCE_CONFIG.avatar_source)
    file_name = f'{uuid4()}.jpg'
    save_path = os.path.join(save_dir, file_name)
    
    # 分批次保存文件，避免大文件占用内存过高
    chunk_size = 1024 * 1024    # 每次读取 1MB
    with open(save_path, 'ab') as fp:
        while True:
            chunk = await avatar_file.read(chunk_size) 
            if not chunk:
                break
            fp.write(chunk)
    # 返回不带http前缀的url地址
    url = '/'.join([ENV_CONFIG.source_prefix, SOURCE_CONFIG.avatar_source, file_name])
    return CommonResponse.success(data={ 'url': url })


@router.post('/change-pwd', openapi_extra=RoutePermission(
        interface_list=[InterfaceEnum.USER_SELF_EDIT]
).to_openapi_extra())
async def update_self_pwd(data: UserChangePasswordSchema, user: UserService.UserModel = Depends(check_permission), session: AsyncSession = Depends(async_session)):
    ''' 更新用户自己的密码接口 '''
    user = await UserService.update_pwd_by_id(getattr(user, 'id'), data, session)
    user_dict = UserSchema.model_validate(user).model_dump()
    return CommonResponse.success(data=user_dict)


@router.post('/dispatch/{uid}', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.USER_MANAGE],
        button_list=[ButtonEnum.USER_DISPATCH_ROLE]
).to_openapi_extra())
async def user_dispatch_role(uid: int, data: UserDispatchRoleSchema, session: AsyncSession = Depends(async_session)) -> CommonResponse:
    logger.info(f'userId: {uid}, data: {data.model_dump()}')
    await UserService.user_dispatch_role(uid, data.rid, session)
    return CommonResponse.success(data=True)


@router.put('/{uid}', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.USER_MANAGE],
        interface_list=[InterfaceEnum.USER_PUT],
        button_list=[ButtonEnum.USER_EDIT]
).to_openapi_extra())
async def update(uid: int, data: UserUpdateSchema, session: AsyncSession = Depends(async_session)) -> CommonResponse:
    logger.info(f'userId: {uid}, data: {data.model_dump()}')
    user = await UserService.update_by_id(uid, data, session)
    return CommonResponse.success(data=UserSchema.model_validate(user).model_dump())


@router.delete('/{uid}', openapi_extra=RoutePermission(
        menu_list=[MenuEnum.USER_MANAGE],
        interface_list=[InterfaceEnum.USER_DEL],
        button_list=[ButtonEnum.USER_DEL]
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
        interface_list=[InterfaceEnum.USER_SELF_GET]
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
        button_list=[ButtonEnum.USER_ADD]
).to_openapi_extra())
async def post(data: UserCreateSchema, session: AsyncSession = Depends(async_session)) -> CommonResponse:
    logger.info(f'data: {data.model_dump()}')
    user = await UserService.create_user(data, session)
    return CommonResponse.success(data=UserSchema.model_validate(user).model_dump())
