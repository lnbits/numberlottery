import asyncio

from fastapi import APIRouter
from lnbits.tasks import create_permanent_unique_task
from loguru import logger

from .crud import db
from .tasks import run_by_the_minute_task, wait_for_paid_invoices
from .views import numberlottery_generic_router
from .views_api import numberlottery_api_router

numberlottery_ext: APIRouter = APIRouter(
    prefix="/numberlottery", tags=["numberlottery"]
)
numberlottery_ext.include_router(numberlottery_generic_router)
numberlottery_ext.include_router(numberlottery_api_router)

numberlottery_static_files = [
    {
        "path": "/numberlottery/static",
        "name": "numberlottery_static",
    }
]

scheduled_tasks: list[asyncio.Task] = []


def numberlottery_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)


def numberlottery_start():
    task1 = create_permanent_unique_task("ext_numberlottery", wait_for_paid_invoices)
    task2 = create_permanent_unique_task(
        "ext_numberlottery_time_check", run_by_the_minute_task
    )
    scheduled_tasks.append(task1)
    scheduled_tasks.append(task2)


__all__ = ["db", "numberlottery_ext", "numberlottery_static_files"]
