import jwt
from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone

from common.log import logger
from common.exception import PermissionException
from common.permission_enum import MenuEnum, InterfaceEnum, ButtonEnum, PermissionEnum

from models.role import RoleModel
from models.permission import PermissionModel


class RoutePermission(BaseModel):
    ''' 路由权限类 '''
    menu_list: list[MenuEnum] = Field(default_factory=list, description='路由对应的菜单权限列表')
    interface_list: list[InterfaceEnum] = Field(default_factory=list, description='路由对应的接口权限列表')
    buttion_list: list[ButtonEnum] = Field(default_factory=list, description='路由对应的按钮权限列表')

    def to_openapi_extra(self) -> dict:
        return {self.get_extra_key(): self.model_dump()}
    
    @classmethod
    def get_extra_key(cls) -> str:
        return 'route_permission'
    
    def is_require_auth(self) -> bool:
        ''' 是否需要权限验证，如果三种权限都为空那么就不需要权限认证 '''
        return any([len(self.menu_list), len(self.interface_list), len(self.buttion_list)])
    
    @classmethod
    def check_items_permission(cls, require_codes: list[str], allow_codes: list[str]) -> bool:
        ''' 两个item对应的权限是否有交集 '''
        # 如果没有定义对应的item，表示不需要权限，直接通过校验
        if not require_codes:
            return True
        print(require_codes, allow_codes, '++++++++++++++++')
        intersection = list(set(require_codes) & set(allow_codes))
        return len(intersection) != 0
    
    @classmethod
    def get_codes(cls, require_items: list[PermissionEnum], allow_items: list[PermissionModel]) -> bool:
        ''' 两个item对应的权限是否有交集 '''
        # 如果没有定义对应的item，表示不需要权限，直接通过校验
        if not require_items:
            return True
        require_codes = [PermissionEnum.get_code(item) for item in require_items]
        allow_codes = [item.code for item in allow_items]
        print(require_codes, allow_codes, '++++++++++++++++')
        intersection = list(set(require_codes) & set(allow_codes))
        return len(intersection) != 0
    
    def check_permission(self, role: RoleModel) -> bool:
        ''' 权限校验逻辑 '''
        # 分别判定route定义的要求在角色的权限中是否存在
        allow_dict = PermissionModel.group_permission(role.permissions)
        require_dict = {'menu': self.menu_list, 'interface': self.interface_list, 'button': self.buttion_list}
        # 如果路由三个权限都不需要，直接通过
        if all([len(permission_list) == 0 for permission_list in require_dict.values()]):
            return True
        # 如果按钮权限不为空，判定有没有按钮权限
        if self.buttion_list and self.check_items_permission(
            PermissionEnum.get_codes(self.buttion_list), 
            [getattr(item, 'code') for item in allow_dict['button']]
        ):
            return True
        
        # 如果接口权限不为空，判定是否有接口权限
        if self.interface_list and self.check_items_permission(
            PermissionEnum.get_codes(self.interface_list), 
            [getattr(item, 'code') for item in allow_dict['interface']]
        ):
            return True
        
        # 如果按钮和接口都没有，那么判定是否有菜单权限
        if (len(self.buttion_list) == len(self.interface_list) == 0) and self.menu_list\
            and self.check_items_permission(
            PermissionEnum.get_codes(self.menu_list), 
            [getattr(item, 'code') for item in allow_dict['menu']]
        ):
            return True

        return False


def generate_token(data: dict, secret_key: str, expire_minutes: int, algorithm: str) -> str:
    ''' 生成jwt令牌 '''
    expire_datetime = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    encode_dict = {'exp': expire_datetime, **data}
    # 这里使用默认算法
    encode_jwt = jwt.encode(encode_dict, secret_key, algorithm)
    return encode_jwt


def parse_token(jwt_token: str, secret_key: str, algorithm: str) -> dict:
    ''' 解析令牌，如果token不正确会抛出权限异常 '''
    try:
        decode_dict = jwt.decode(jwt_token, secret_key, algorithms=[algorithm])
        now_timestamp = datetime.now(timezone.utc).timestamp()
        if 'exp' not in decode_dict:
            raise PermissionException('异常的令牌')
        
        if decode_dict['exp'] < now_timestamp:
            raise PermissionException('失效的令牌')
        decode_dict.pop('exp')
        return decode_dict
    except jwt.ExpiredSignatureError as e:
        logger.exception(e)
        raise PermissionException('登录过期，请重新登录')
    except Exception as e:
        logger.exception(e)
        raise PermissionException('非法的令牌')
