import services.role as RoleServer
import services.user as UserServer
import services.permission as PermissionServer

from config import AUTH_CONFIG
from models.enums import PermissionEnum
from db import AsyncSession, async_session_wrapper

from schemas.role import RoleCreateSchema
from schemas.user import UserCreateSchema
from schemas.permission import PermissionCreateSchema

from common.log import logger
from common.permission_enum import PermissionEnum as PermissionDetailEnum, MenuEnum, InterfaceEnum, ButtionEnum


########################### 初始化权限相关内容 ###########################
async def insert_by_enum(pe: type[PermissionDetailEnum], type: PermissionEnum, session: AsyncSession):
    for item in pe.all():
        data = PermissionCreateSchema(**item.model_dump(), type=type)
        try:
            await PermissionServer.create_obj(data, session)
            logger.info(f'inser {data.name}:{data.code} success!')
        except Exception as e:
            logger.error(f'insert data: {data.model_dump()} fail, detail is {e}')


@async_session_wrapper
async def insert_permission(*args, **kwargs):
    session: AsyncSession = kwargs['session']
    await insert_by_enum(MenuEnum, PermissionEnum.MENU, session)
    await insert_by_enum(InterfaceEnum, PermissionEnum.INTERFACE, session)
    await insert_by_enum(ButtionEnum, PermissionEnum.BUTTON, session)


########################### 初始化角色相关内容 ###########################
@async_session_wrapper
async def build_superadmin_role(*args, **kwargs):
    ''' 创建超级管理员角色 '''
    session: AsyncSession = kwargs['session']
    
    # 查询超级管理员角色，没有就创建
    role = await RoleServer.get_obj_by_query({'code': AUTH_CONFIG.manage.super_admin_code}, session)
    if not role:
        data = RoleCreateSchema(
            name=AUTH_CONFIG.manage.super_admin_name,
            code=AUTH_CONFIG.manage.super_admin_code,
            desc=AUTH_CONFIG.manage.super_admin_desc,
            enable=True    
        )
        role = await RoleServer.create_obj(data, session)
    
    permission_list = await PermissionServer.all_permission_list_by_enable(session=session)
    role.permissions = list(permission_list)
    await session.commit()
    await session.refresh(role)


########################### 初始化用户相关内容 ###########################
@async_session_wrapper
async def create_superadmin(*args, **kwargs):
    ''' 创建超级管理员 '''
    session: AsyncSession = kwargs['session']
    name, pwd = map(kwargs.get, ('name', 'password'))
    if not all([name, pwd]):
        raise Exception('用户名或者密码为空')
    
    # 查询超级管理员角色，没有就创建
    role = await RoleServer.get_obj_by_query({'code': AUTH_CONFIG.manage.super_admin_code}, session)
    if not role:
        data = RoleCreateSchema(
            name=AUTH_CONFIG.manage.super_admin_name,
            code=AUTH_CONFIG.manage.super_admin_code,
            desc=AUTH_CONFIG.manage.super_admin_desc,
            enable=True
        )
        role = await RoleServer.create_obj(data, session)
    
    data = {'name': name, 'password': pwd, 'rid': getattr(role, 'id')}
    super_admin_user_data = UserCreateSchema(**data)
    user = await UserServer.create_user(super_admin_user_data, session)
    await UserServer.user_dispatch_role(getattr(user, 'id'), getattr(role, 'id'), session)
