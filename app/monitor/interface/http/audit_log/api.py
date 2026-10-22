"""审计日志查询路由。"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.utils.schemas import PageResult
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.interface.http.dependencies import get_current_user
from app.monitor.application.audit_log.services import AuditLogApplicationService
from app.monitor.interface.dependences import get_audit_log_app_service
from app.monitor.interface.http.audit_log.schemas import AuditLogResp, GetAuditLogsReq

audit_log_router = APIRouter(prefix='/audit-logs', tags=['审计日志'])


@audit_log_router.get('', response_model=PageResult[AuditLogResp],
                      summary='审计日志列表')
async def list_audit_logs(
    filters: Annotated[GetAuditLogsReq, Query()],
    current_user: CurrentUser = Depends(get_current_user),
    app_service: AuditLogApplicationService = Depends(get_audit_log_app_service),
) -> PageResult[AuditLogResp]:
    page = await app_service.get_page(filters, current_user)
    return PageResult[AuditLogResp](
        page=page.page,
        page_size=page.page_size,
        total=page.total,
        data=[AuditLogResp(**item.model_dump()) for item in (page.data or [])],
    )
