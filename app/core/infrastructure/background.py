"""进程内后台任务门面：注册 / 启动 / 停止。

只承载「自主驱动 × 同进程」的常驻任务——没有外部消息可等、自己按时间或状态
持续运行的那一类。消息消费走事件总线，跨进程任务另立 worker。

模块在 bootstrap() 阶段 register()，core.start() 在模块钩子之后统一 start_all()，
core.stop() 在释放基础设施之前 stop_all()（逆序）。任务契约只有 start/stop，
循环、间隔、异常处理由各任务自己实现（不抽基类）。
"""
from typing import Protocol

from loguru import logger


class BackgroundTask(Protocol):
    """常驻后台任务契约。"""

    async def start(self) -> None: ...

    async def stop(self) -> None: ...


_tasks: list[BackgroundTask] = []


def register(task: BackgroundTask) -> None:
    """登记一个常驻任务；须在模块 bootstrap 阶段调用。"""
    _tasks.append(task)


async def start_all() -> None:
    """按注册顺序启动全部任务；任一启动失败则启动流程中断。"""
    for task in _tasks:
        await task.start()


async def stop_all() -> None:
    """逆序停止；单个任务失败记日志，不阻断其他任务。"""
    for task in reversed(_tasks):
        try:
            await task.stop()
        except Exception:
            logger.exception('后台任务停止失败：{}', type(task).__name__)
