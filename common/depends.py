from typing import cast, Annotated
from fastapi.routing import APIRoute
from fastapi import Request, Header, Depends

from config import AUTH_CONFIG
from db import AsyncSession, async_session

from common.utils import get_model_fields
from common.auth import RoutePermission, parse_token
from common.pagination import PaginationQuerySchema
from common.exception import PermissionException, ApiException

from models.role import RoleModel
from services import user as UserService


async def get_query_params(request: Request) -> PaginationQuerySchema:
    ''' 收集所有查询参数​并处理 '''
    query_params = dict(request.query_params)   # 获取所有查询参数​
    fields = [field for field in get_model_fields(PaginationQuerySchema) if field != 'query']
    query_dict, data_dict = {}, {}
    for k, v in query_params.items():
        if k in fields:
            data_dict[k] = v
        else:
            query_dict[k] = v
    pagination_query = PaginationQuerySchema(**data_dict, query=query_dict)
    return pagination_query


async def check_permission(request: Request, Authorization: Annotated[str, Header()] = '', session: AsyncSession = Depends(async_session)):
    ''' 从请求中获取接口定义时附加的参数，判断是否允许访问
    权限分三种:菜单权限,接口权限和按钮权限
    '''
    # 获取当前路由的端点信息（包含定义时的参数）
    route: APIRoute = cast(APIRoute, request.scope.get('route'))
    if not route:
        raise PermissionException('没有权限')
    # 没有额外参数 ===> 不需要权限
    if not route.openapi_extra:
        return
    
    route_permission = RoutePermission(**route.openapi_extra.get(RoutePermission.get_extra_key(), {}))
    if not route_permission.is_require_auth():
        return
    
    # 需要校验权限，判定用户是否有对应路由所定义的权限
    user_dict = parse_token(Authorization, AUTH_CONFIG.jwt.secret_key, AUTH_CONFIG.jwt.algorithm)
    print(route_permission.model_dump(), '==============')
    user_obj = await UserService.get_obj_by_query({ 'id': user_dict.get('id') }, session)
    if not user_obj:
        raise PermissionException('用户不存在')
    
    if not user_obj.role:
        raise PermissionException('未知角色，没有权限访问')
    role: RoleModel = user_obj.role
    # 基于路由权限需要基于角色判定是否有权限访问
    if not route_permission.check_permission(role):
        raise ApiException('没有权限')
    return user_obj
