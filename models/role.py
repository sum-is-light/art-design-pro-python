from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from db import DBBaseModel
from models.permission import PermissionModel
from models.role_permission import RolePermissionModel


class RoleModel(DBBaseModel):
    ''' 角色模型 '''
    __tablename__ = 'role'

    name = Column(String(255), nullable=False, comment='角色名称')
    code = Column(String(255), nullable=False, comment='角色编码')
    desc = Column(String(512), comment='角色描述')

    ############## 关联关系 ##############
    users = relationship('UserModel', back_populates='role')    # 用户与角色是一对一关系
    permissions = relationship(                                 # 角色与权限是多对多关系
        'PermissionModel',
        secondary=RolePermissionModel.__table__,
        back_populates='roles', lazy='selectin'
    )

    def get_permission_codes(self, key: str | None) -> list[str]:
        permissions: list[PermissionModel] = self.permissions
        if key is None:
            return [getattr(p, 'code') for p in permissions]
        permission_dict = PermissionModel.group_permission(permissions)
        if key in permission_dict:
            return [getattr(p, 'code') for p in permission_dict[key]]
        return []
