from fastapi import APIRouter

# 用户资源路由（前缀由资源定；模块前缀 /iam 由 app 工厂统一加）
user_router = APIRouter(prefix='/users', tags=['用户'])
