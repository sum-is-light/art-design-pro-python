'''
权限分三种, 他们的详细介绍如下:
- 菜单权限: 控制页面能看到哪些部分的权限
- 接口权限: 控制能访问那些接口的权限
- 按钮权限: 控制页面能使用那些按钮的权限
'''
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PermissionEnumValue(BaseModel):
    ''' 权限枚举值类,用于数据库数据构建提供更详细的信息 '''
    name: str = Field(description='权限名称')
    code: str = Field(description='权限唯一标识')
    desc: Optional[str] = Field(default=None, description='权限描述')


class PermissionEnum(Enum):
    ''' 权限枚举 '''

    @classmethod
    def all(cls) -> list[PermissionEnumValue]:
        return [permission.value for permission in cls.__members__.values()]


class MenuEnum(PermissionEnum):
    ''' 菜单权限枚举 '''
    USER_MANAGE = PermissionEnumValue(name='用户管理', code='user-manage')
    ROLE_MANAGE = PermissionEnumValue(name='角色管理', code='role-manage')
    PERMISSION_MANAGE = PermissionEnumValue(name='权限管理', code='permission-manage')


class InterfaceEnum(PermissionEnum):
    ''' 接口权限枚举 '''
    USER_GET = PermissionEnumValue(name='创建用户信息', code='/users/get')
    USER_POST = PermissionEnumValue(name='创建用户', code='/users/post')
    USER_PUT = PermissionEnumValue(name='修改用户信息', code='/users/put')
    USER_DEL = PermissionEnumValue(name='删除用户信息', code='/users/delete')
    USER_ENABLE = PermissionEnumValue(name='用户启用禁用', code='/users/delete')


class ButtionEnum(PermissionEnum):
    ''' 按钮权限枚举 '''
    USER_ADD = PermissionEnumValue(name='用户新增', code='user:add')
    USER_EDIT = PermissionEnumValue(name='用户编辑', code='user:edit')
    USER_DEL = PermissionEnumValue(name='用户删除', code='user:del')

    ROLE_ADD = PermissionEnumValue(name='权限新增', code='role:add')
    ROLE_EDIT = PermissionEnumValue(name='权限编辑', code='role:edit')
    ROLE_DEL = PermissionEnumValue(name='权限删除', code='role:del')

    PERMISSION_ADD = PermissionEnumValue(name='权限新增', code='role:add')
    PERMISSION_EDIT = PermissionEnumValue(name='权限编辑', code='role:edit')
    PERMISSION_DEL = PermissionEnumValue(name='权限删除', code='role:del')

# print(MenuEnum.all())
