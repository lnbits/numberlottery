import asyncio

from fastapi import APIRouter
from lnbits.tasks import create_permanent_unique_task
from loguru import logger

from .crud import db
from .tasks import run_by_the_minute_task, wait_for_paid_invoices
from .views import numbers_generic_router
from .views_api import numbers_api_router

numbers_ext: APIRouter = APIRouter(prefix="/numbers", tags=["numbers"])
numbers_ext.include_router(numbers_generic_router)
numbers_ext.include_router(numbers_api_router)

numbers_static_files = [
    {
        "path": "/numbers/static",
        "name": "numbers_static",
    }
]

scheduled_tasks: list[asyncio.Task] = []


def numbers_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)


def numbers_start():
    task1 = create_permanent_unique_task("ext_numbers", wait_for_paid_invoices)
    task2 = create_permanent_unique_task(
        "ext_numbers_time_check", run_by_the_minute_task
    )
    scheduled_tasks.append(task1)
    scheduled_tasks.append(task2)


__all__ = ["db", "numbers_ext", "numbers_static_files"]
