from pydantic import BaseModel

from db import DBBaseModel
from common.log import logger


def get_db_model_fields(model: type[DBBaseModel]) -> list[str]:
    ''' 基于给定的数据库模型获取其定义的字段 '''
    return list(model.__table__.columns.keys())


def get_model_fields(model: type[BaseModel]) -> list[str]:
    ''' 基于给定的pydantic模型返回字段列表 '''
    try:
        return list(model.model_fields.keys())
    except Exception as e:
        logger.warning('Pydantic Version < 2, please update it!')
        return list(model.__fields__.keys())
