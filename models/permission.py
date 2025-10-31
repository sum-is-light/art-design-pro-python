from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Enum

from db import DBBaseModel
from models.enums import PermissionEnum
from models.role_permission import RolePermissionModel


class PermissionModel(DBBaseModel):
    ''' 权限模型 '''
    __tablename__ = 'permission'

    name = Column(String(255), nullable=False, comment='权限名')
    code = Column(String(255), nullable=False, comment='权限编码')
    type  = Column(Enum(PermissionEnum, create_type=True), comment='权限类型')
    desc = Column(String(512), comment='权限描述')

    ############## 关联关系 ##############
    roles = relationship(
        'RoleModel',
        secondary=RolePermissionModel.__table__,
        back_populates='permissions',
        lazy='selectin'
    )

    @classmethod
    def group_permission(cls, permissions: list['PermissionModel']) -> dict[str, list['PermissionModel']]:
        permission_dict = {'menu': [], 'interface': [], 'button': []}
        for obj in permissions:
            if getattr(obj, 'type') == PermissionEnum.MENU:
                permission_dict['menu'].append(obj)
            elif getattr(obj, 'type') == PermissionEnum.INTERFACE:
                permission_dict['interface'].append(obj)
            elif getattr(obj, 'type') == PermissionEnum.BUTTON:
                permission_dict['button'].append(obj)
        return permission_dict
