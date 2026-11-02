"""HTTP 异常处理：把异常族的语义**在此处**映射为 HTTP 状态码 + 统一错误体。

约定：
- 业务异常 → 4xx，状态码由 ``kind`` 决定（见 ``_KIND_TO_STATUS``）；
- 技术中立异常 / 未捕获异常 → 500，不向客户端泄露内部信息，日志带堆栈。
统一错误体：``{"code": str, "message": str, "details": any}``。
"""
from fastapi import status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import (
    BusinessBaseException,
    ErrorKindEnum,
    InfrastructureBaseException,
)


_KIND_TO_STATUS: dict[ErrorKindEnum, int] = {
    ErrorKindEnum.VALIDATION: status.HTTP_400_BAD_REQUEST,
    ErrorKindEnum.UNAUTHENTICATED: status.HTTP_401_UNAUTHORIZED,
    ErrorKindEnum.FORBIDDEN: status.HTTP_403_FORBIDDEN,
    ErrorKindEnum.NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorKindEnum.CONFLICT: status.HTTP_409_CONFLICT,
}


def _error_response(status_code: int, code: str, message: str, details=None) -> JSONResponse:
    return JSONResponse(
        jsonable_encoder({'code': code, 'message': message, 'details': details}),
        status_code=status_code,
    )


async def business_exception_handler(request: Request, exc: BusinessBaseException) -> JSONResponse:
    """业务异常（预期内）→ 4xx。"""
    logger.warning(f'{type(exc).__name__}: {exc}')
    return _error_response(
        _KIND_TO_STATUS.get(exc.kind, status.HTTP_400_BAD_REQUEST),
        exc.code,
        str(exc),
        exc.details,
    )


async def infrastructure_exception_handler(request: Request, exc: InfrastructureBaseException) -> JSONResponse:
    """技术中立异常 → 500。"""
    logger.opt(exception=exc).error(f'基础设施异常：{exc}')
    return _error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, 'SERVER_ERROR', '服务器错误')


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """归一 FastAPI 请求校验错误（默认形状 {"detail": [...]}）到统一错误体。"""
    return _error_response(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        'REQUEST_VALIDATION_ERROR',
        '请求参数校验失败',
        exc.errors(),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """归一 Starlette/FastAPI 的 HTTPException（未知路由 404、405 等）。"""
    return _error_response(exc.status_code, 'HTTP_ERROR', str(exc.detail))


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """兜底（含程序 bug）→ 500。"""
    logger.opt(exception=exc).error(f'未捕获异常：{exc}')
    return _error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, 'SERVER_ERROR', '服务器错误')
