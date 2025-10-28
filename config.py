import toml
from pydantic import BaseModel, Field


class EnvConfig(BaseModel):
    ''' 环境配置 '''
    host: str = Field(description='主机地址')
    port: int = Field(description='端口号')
    workers: int = Field(description='线程数')
    debug: bool = Field(description='是否开启调试模式')


class LogConfig(BaseModel):
    ''' 日志配置 '''
    level: str = Field(description='日志等级')
    format: str = Field(description='日志格式')
    file: str = Field(description='日志保存位置')


class DBConfig(BaseModel):
    ''' 数据库配置 '''
    url: str = Field(description='数据库连接地址')
    echo: bool = Field(description='是否打印SQL语句')


class AuthJWTConfig(BaseModel):
    ''' 权限Token配置 '''
    secret_key: str = Field(description='jwt密钥')
    algorithm: str = Field(description='算法')
    expire_minute: int = Field(description='过期时间')


class AuthManageConfig(BaseModel):
    ''' 权限管理配置 '''
    super_admin_name: str = Field(description='超级管理员名称')
    super_admin_code: str = Field(description='超级管理员编码')
    super_admin_desc: str = Field(description='超级管理员描述')


class AuthConfig(BaseModel):
    ''' 权限配置 '''
    jwt: AuthJWTConfig = Field(description='jwt配置')
    manage: AuthManageConfig = Field(description='权限管理配置')


class Config(BaseModel):
    ''' 配置类 '''
    env: EnvConfig = Field(description='环境配置')
    log: LogConfig = Field(description='日志配置')
    db: DBConfig = Field(description='数据库配置')
    auth: AuthConfig = Field(description='权限配置')


######################## 加载配置并导出常用配置 ########################
with open('config.toml', 'r', encoding='utf-8') as fp:
    CONFIG = Config(**toml.load(fp))

ENV_CONFIG = CONFIG.env
LOG_CONFIG = CONFIG.log
DB_CONFIG = CONFIG.db
AUTH_CONFIG = CONFIG.auth
