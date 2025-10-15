from passlib.context import CryptContext
from sqlalchemy import Column, String, Enum

from db import DBBaseModel
from .enums import GenderEnum

class UserModel(DBBaseModel):
    ''' 用户模型 '''
    __tablename__ = 'user'

    name = Column(String(255), nullable=False, comment='用户名')
    nickname = Column(String(255), comment='昵称')
    hashed_password = Column(String(255), nullable=False, comment='加密后的密码')
    gender = Column(Enum(GenderEnum, create_type=True), default=GenderEnum.UNKNOWN, comment='性别')
    email = Column(String(255), comment='邮箱')
    phone = Column(String(25), comment='手机号')
    avatar = Column(String(255), comment='头像地址')
    address = Column(String(255), comment='地址')
    introduce = Column(String(512), comment='个人介绍')

    pwd_context = CryptContext(
        schemes=["bcrypt"],  # 使用 bcrypt 算法
        deprecated="auto"    # 自动处理过时的加密方案
    )

    @property
    def password(self) -> str:
        return str(self.hashed_password)
    
    @password.setter
    def password(self, value: str):
        self.hashed_password = self.pwd_context.hash(value)

    def check_pwd(self, pwd: str) -> bool:
        ''' 校验密码是否合法 '''
        return self.pwd_context.verify(pwd, self.password)
