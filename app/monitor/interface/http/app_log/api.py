"""应用日志路由：归档列表 / 查看 / 下载 / 实时 tail / 手动归档。"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import PlainTextResponse, StreamingResponse

from app.monitor.application.app_log.services import AppLogApplicationService
from app.monitor.application.common.dto import CurrentUser
from app.monitor.interface.dependences import get_app_log_app_service
from app.monitor.interface.http.app_log.schemas import AppLogFileResp, GetAppLogsReq
from app.monitor.interface.http.dependencies import get_current_user

app_log_router = APIRouter(prefix='/app-logs', tags=['应用日志'])

# 查看时最多返回的字节数；超出提示下载
_MAX_VIEW_BYTES = 5 * 1024 * 1024


@app_log_router.get('', response_model=list[AppLogFileResp],
                    summary='归档日志列表')
async def list_app_logs(
    filters: Annotated[GetAppLogsReq, Query()],
    current_user: CurrentUser = Depends(get_current_user),
    app_service: AppLogApplicationService = Depends(get_app_log_app_service),
) -> list[AppLogFileResp]:
    items = await app_service.list_files(filters, current_user)
    return [AppLogFileResp(**item.model_dump()) for item in items]


@app_log_router.get('/view', response_class=PlainTextResponse,
                    summary='查看归档日志（文本）')
async def view_app_log(
    key: str = Query(...),
    current_user: CurrentUser = Depends(get_current_user),
    app_service: AppLogApplicationService = Depends(get_app_log_app_service),
) -> PlainTextResponse:
    data = await app_service.read_file(key, current_user)
    truncated = len(data) > _MAX_VIEW_BYTES
    text = data[:_MAX_VIEW_BYTES].decode('utf-8', errors='replace')
    if truncated:
        text += '\n\n...（文件过大，已截断，请下载查看）'
    return PlainTextResponse(text)


@app_log_router.get('/download', summary='下载归档日志')
async def download_app_log(
    key: str = Query(...),
    current_user: CurrentUser = Depends(get_current_user),
    app_service: AppLogApplicationService = Depends(get_app_log_app_service),
) -> Response:
    data = await app_service.read_file(key, current_user)
    filename = key.rsplit('/', 1)[-1] or 'log.txt'
    return Response(
        data,
        media_type='application/octet-stream',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    )


@app_log_router.get('/tail', summary='实时日志（SSE）')
async def tail_app_log(
    file: str = Query('app', pattern='^(app|error)$'),
    current_user: CurrentUser = Depends(get_current_user),
    app_service: AppLogApplicationService = Depends(get_app_log_app_service),
) -> StreamingResponse:
    stream = await app_service.stream(file, current_user)
    return StreamingResponse(
        stream,
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        },
    )


@app_log_router.post('/archive', status_code=202, summary='手动触发日志归档')
async def archive_app_logs(
    current_user: CurrentUser = Depends(get_current_user),
    app_service: AppLogApplicationService = Depends(get_app_log_app_service),
) -> Response:
    await app_service.trigger_archive(current_user)
    return Response(status_code=202)
