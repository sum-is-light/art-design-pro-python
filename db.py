from datetime import datetime
from typing import Optional, Type
from uuid import UUID as UUID4, uuid4
from pydantic import BaseModel, Field, field_validator, ConfigDict

from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import Column, UUID, DateTime, Boolean, Integer, JSON

from config import DB_CONFIG

SQLALCHEMY_DATABASE_URL = DB_CONFIG.url
async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=DB_CONFIG.echo,    # 是否打印 SQL
    future=True,            # 使用 SQLAlchemy 2.0 特性
    pool_pre_ping=True      # 检测连接有效性
)

# 异步会话工厂（每次请求对应一个会话）
AsyncSessionLocal = sessionmaker(
    bind=async_engine,      # type: ignore[arg-type]
    class_=AsyncSession,    # type: ignore[arg-type]
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)
Base = declarative_base()


class DBBaseModel(Base):
    ''' 数据基本模型 '''
    __abstract__ = True     # 抽象类不会被实例化

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键')
    uuid = Column(UUID, default=uuid4, comment='UUID标识')
    ctime = Column(DateTime, default=datetime.now, comment='创建时间')
    utime = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    created_by = Column(Integer, nullable=True, comment='创建者ID')
    updated_by = Column(Integer, nullable=True, comment='更新者ID')
    is_delete = Column(Boolean, default=False, comment='是否删除')
    enable = Column(Boolean, default=True, comment='是否可用')
    meta = Column(JSON, comment='附加信息')

    @classmethod
    def get_default_sort(cls) -> tuple:
        return (cls.utime.desc(), cls.ctime.desc(), cls.id.asc())


class DBBaseSchema(BaseModel):
    ''' 数据基本模型 '''
    id: int = Field(description='主键')
    uuid: UUID4 = Field(description='UUID标识')
    ctime: datetime = Field(description='创建时间')
    utime: datetime = Field(description='更新时间')
    created_by: Optional[int] = Field(description='创建者')
    updated_by: Optional[int] = Field(description='更新者')
    enable: bool = Field(description='是否可用')

    # 添加模型配置，允许未知类型 适配Pydantic v2
    model_config = ConfigDict(
        arbitrary_types_allowed=True,   # 允许 Pydantic 不认识的类型
        from_attributes=True            # 如果需要从 ORM 模型转换，加上这个（v2 用 from_attributes，v1 用 orm_mode）
    )

    @field_validator('ctime', 'utime', mode='before')
    def format_datetime(cls, value: datetime) -> str:
        if not isinstance(value, datetime):
            return value
        return value.strftime('%Y-%m-%d %H:%M:%S')


async def async_session():
    ''' 获取异步session '''
    async with AsyncSessionLocal() as session:  # type: ignore[arg-type]
        yield session


def async_session_wrapper(func):
    ''' 获取异步session的装饰器 '''
    async def wrapper(*args, **kwargs):
        async with AsyncSessionLocal() as session:  # type: ignore[arg-type]
            kwargs['session'] = session
            return await func(*args, **kwargs)
    
    return wrapper
