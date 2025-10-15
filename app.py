from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError

from apis import router_list
from db import async_engine, DBBaseModel
from common.log import logger
from common.auth import check_permission
from common.middleware import handle_exception_middleware, handler_validation_exception


@asynccontextmanager
async def lifespan(app: FastAPI):
    # app启动前执行的操作
    async with async_engine.begin() as connect:
        logger.info(f'init tables, {DBBaseModel.metadata}')
        await connect.run_sync(DBBaseModel.metadata.create_all)
    yield
    # app启动后执行的操作


def create_app() -> FastAPI:
    # 添加通用权限处理依赖
    app = FastAPI(lifespan=lifespan, dependencies=[Depends(check_permission)])

    # 为app添加路由
    for route_info in router_list:
        app.include_router(
            prefix=route_info.prefix,
            router=route_info.router,
            tags=route_info.tags
        )
    
    # 添加自定义中间件
    app.middleware('http')(handle_exception_middleware)
    app.exception_handler(RequestValidationError)(handler_validation_exception)
    return app
