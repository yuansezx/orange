import uvicorn

from app.core.infrastructure.settings import CORE_SETTINGS

if __name__ == "__main__":
    uvicorn.run('app:create_app', factory=True, host=CORE_SETTINGS.host, port=CORE_SETTINGS.port)
    # uvicorn.run('app:create_app', factory=True, host='0.0.0.0', port=8500, reload=False)
