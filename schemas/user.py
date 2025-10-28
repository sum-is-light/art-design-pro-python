from typing import Optional
from pydantic import BaseModel, Field

from db import DBBaseSchema
from models.enums import GenderEnum


class UserSchema(DBBaseSchema):
    name: str = Field(description='用户名')
    nickname: Optional[str] = Field(description='昵称')
    gender: GenderEnum = Field(description='性别')
    email: Optional[str] = Field(description='邮箱')
    phone: Optional[str] = Field(description='手机号')
    avatar: Optional[str] = Field(description='头像地址')
    address: Optional[str] = Field(description='地址')
    introduce: Optional[str] = Field(description='个人介绍')


class UserLoginSchema(BaseModel):
    name: str = Field(description='用户名')
    password: str = Field(min_length=4, max_length=24, description='密码')


class UserChangeStatusSchema(BaseModel):
    enable: bool = Field(description='是否启用')


class UserDispatchRoleSchema(BaseModel):
    rid: int = Field(description='角色ID')


class UserUpdateSchema(BaseModel):
    name: Optional[str] = Field(default=None, description='用户名')
    nickname: Optional[str] = Field(default=None, description='昵称')
    gender: Optional[GenderEnum] = Field(default=None, description='性别')
    email: Optional[str] = Field(default=None, description='邮箱')
    phone: Optional[str] = Field(default=None, description='手机号')
    avatar: Optional[str] = Field(default=None, description='头像地址')
    address: Optional[str] = Field(default=None, description='地址')
    introduce: Optional[str] = Field(default=None, description='个人介绍')


class UserCreateSchema(BaseModel):
    name: str = Field(description='用户名')
    password: str = Field(min_length=4, max_length=24, description='密码')
    nickname: Optional[str] = Field(default=None, description='昵称')
    gender: Optional[GenderEnum] = Field(default=None, description='性别')
    email: Optional[str] = Field(default=None, description='邮箱')
    phone: Optional[str] = Field(default=None, description='手机号')
    avatar: Optional[str] = Field(default=None, description='头像地址')
    address: Optional[str] = Field(default=None, description='地址')
    introduce: Optional[str] = Field(default=None, description='个人介绍')
