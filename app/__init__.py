from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import core
from app.core.exceptions import global_exception_handler


# fastapi 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    await core.start()

    yield

    await core.stop()


def create_app():
    app = FastAPI(title='代码库', lifespan=lifespan)
    # 注册全局异常处理函数
    app.add_exception_handler(Exception, global_exception_handler)

    # # cors
    # app.add_middleware(CORSMiddleware, allow_origins=CORE_SETTINGS.cors_allowed_origins, allow_credentials=True,
    #                    allow_methods=["*"], allow_headers=["*"])

    # 挂载路由


    return app


main_app = create_app()