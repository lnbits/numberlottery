from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer

from .crud import get_numbers

numbers_generic_router: APIRouter = APIRouter()


def numbers_renderer():
    return template_renderer(["numbers/templates"])


@numbers_generic_router.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return numbers_renderer().TemplateResponse(
        "numbers/index.html", {"request": request, "user": user.json()}
    )


@numbers_generic_router.get("/{numbers_id}", response_class=HTMLResponse)
async def display_numbers(request: Request, numbers_id: str):
    numbers = await get_numbers(numbers_id)
    return numbers_renderer().TemplateResponse(
        "numbers/numbers.html",
        {
            "numbers_id": numbers_id,
            "completed": numbers.completed,
            "height_number": numbers.completed,
            "block_height": numbers.completed,
            "request": request,
        },
    )
