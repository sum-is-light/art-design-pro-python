import time
from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.responses import Response, JSONResponse

from common.log import logger
from common.response import CommonResponse
from common.exception import PermissionException, ApiException

async def handle_exception_middleware(request: Request, call_next):
    ''' 处理异常为统一格式的中间件 '''
    start_tm = time.time_ns()
    client_info = f'{request.client.host}:{request.client.port}' if request.client else 'unknown'
    logger.info(f'{client_info} - {request.method.upper()} {request.url.path}?{request.query_params} {request.url.scheme.upper()}')
    try:
        resp: Response = await call_next(request)
    except PermissionException as e:
        logger.error(e)
        resp = JSONResponse(
            status_code=200, content=CommonResponse.fail(e.code, str(e)).model_dump()
        )
    except HTTPException as e:
        logger.error(e)
        resp = JSONResponse(
            status_code=200, content=CommonResponse.fail(e.status_code, f'HTTP异常!\ndetail: {e.detail}').model_dump()
        )
    except ApiException as e:
        logger.error(e)
        resp = JSONResponse(
            status_code=200, content=CommonResponse.fail(500, f'接口异常,请联系管理员!\ndetail: {e}').model_dump()
        )
    except Exception as e:
        logger.exception(e)
        resp = JSONResponse(
            status_code=200, content=CommonResponse.fail(500, f'未知异常,请联系管理员!\ndetail: {e}').model_dump()
        )
    finally:
        end_tm = time.time_ns()
    logger.info(f'{client_info} - {request.method.upper()} {request.url.path}?{request.query_params} {request.url.scheme.upper()} status code:{resp.status_code}, processing time:{(end_tm - start_tm) // 1e6:.0f}ms')
    return resp


async def handler_validation_exception(request: Request, exc: RequestValidationError):
    ''' 处理参数验证失败的异常 '''
    logger.error(exc)   # 显示日志
    return JSONResponse(
        status_code=200,
        content=CommonResponse.fail(501, str(exc)).model_dump()
    )
