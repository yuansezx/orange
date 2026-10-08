from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import core
from app.core.exceptions import BusinessBaseException, InfrastructureBaseException
from app.interface.http.exception_handlers import (
    business_exception_handler,
    global_exception_handler,
    http_exception_handler,
    infrastructure_exception_handler,
    validation_exception_handler,
)


# fastapi 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    await core.start()

    yield

    await core.stop()


def create_app():
    app = FastAPI(title='代码库', lifespan=lifespan)
    # 注册全局异常处理函数（按异常类型/MRO 匹配，非顺序）
    app.add_exception_handler(BusinessBaseException, business_exception_handler)
    app.add_exception_handler(InfrastructureBaseException, infrastructure_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)

    # # cors
    # app.add_middleware(CORSMiddleware, allow_origins=CORE_SETTINGS.cors_allowed_origins, allow_credentials=True,
    #                    allow_methods=["*"], allow_headers=["*"])

    # 挂载路由

    return app
