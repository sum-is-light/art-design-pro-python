from typing import Optional
from pydantic import BaseModel, Field

from db import DBBaseSchema
from models.permission import PermissionEnum


class PermissionSchema(DBBaseSchema):
    name: str = Field(description='权限名')
    code: str = Field(description='权限编码')
    type: PermissionEnum = Field(description='权限类型')
    desc: Optional[str] = Field(description='权限描述')


class PermissionUpdateSchema(BaseModel):
    desc: Optional[str] = Field(default=None, description='权限描述')


class PermissionCreateSchema(BaseModel):
    name: str = Field(description='角色名称')
    code: str = Field(description='角色编码')
    type: PermissionEnum = Field(description='权限类型')
    desc: Optional[str] = Field(description='权限描述')
