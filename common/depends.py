from fastapi import Request
from common.pagination import PaginationQuerySchema
from common.utils import get_model_fields

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
