from typing import Optional
from pydantic import BaseModel, Field

from db import DBBaseSchema


class RoleSchema(DBBaseSchema):
    name: str = Field(description='角色名称')
    code: str = Field(description='角色编码')
    desc: Optional[str] = Field(description='角色描述')


class RoleUpdateSchema(BaseModel):
    name: str = Field(description='角色名称')
    code: str = Field(description='角色编码')
    enable: Optional[bool] = Field(default=None, description='是否启用')
    desc: Optional[str] = Field(default=None, description='角色描述')


class RoleUpdatePermissionSchema(BaseModel):
    permission_ids: list[int] = Field(description='权限Id列表')


class RoleCreateSchema(BaseModel):
    name: str = Field(description='角色名称')
    code: str = Field(description='角色编码')
    enable: bool = Field(description='是否启用')
    desc: Optional[str] = Field(description='角色描述')
