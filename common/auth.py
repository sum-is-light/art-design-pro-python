import jwt
from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone

from common.log import logger
from common.exception import PermissionException
from common.permission_enum import MenuEnum, InterfaceEnum, ButtionEnum


class RoutePermission(BaseModel):
    ''' 路由权限类 '''
    menu_list: list[MenuEnum] = Field(default_factory=list, description='路由对应的菜单权限列表')
    interface_list: list[InterfaceEnum] = Field(default_factory=list, description='路由对应的接口权限列表')
    buttion_list: list[ButtionEnum] = Field(default_factory=list, description='路由对应的按钮权限列表')

    def to_openapi_extra(self) -> dict:
        return {self.get_extra_key(): self.model_dump()}
    
    @classmethod
    def get_extra_key(cls) -> str:
        return 'route_permission'
    
    def is_require_auth(self) -> bool:
        ''' 是否需要权限验证，如果三种权限都为空那么就不需要权限认证 '''
        return any([len(self.menu_list), len(self.interface_list), len(self.buttion_list)])
    
    def check_menu(self, code: str) -> bool:
        ''' 检查菜单权限 '''
        # 如果对应权限列表为空,表示对该权限不做限制,直接返回
        if not self.menu_list:
            return True
        return code in [item.value.code for item in self.menu_list]
    
    def chek_interface(self, code: str) -> bool:
        ''' 检查接口权限 '''
        # 如果对应权限列表为空,表示对该权限不做限制,直接返回
        if not self.interface_list:
            return True
        return code in [item.value.code for item in self.interface_list]
    
    def chek_button(self, code: str) -> bool:
        ''' 检查按钮权限 '''
        # 如果对应权限列表为空,表示对该权限不做限制,直接返回
        if not self.buttion_list:
            return True
        return code in [item.value.code for item in self.buttion_list]



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
