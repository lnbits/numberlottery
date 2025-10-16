from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer

numberlottery_generic_router: APIRouter = APIRouter()


def numberlottery_renderer():
    return template_renderer(["numberlottery/templates"])


@numberlottery_generic_router.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return numberlottery_renderer().TemplateResponse(
        "numberlottery/index.html", {"request": request, "user": user.json()}
    )


@numberlottery_generic_router.get("/{game_id}", response_class=HTMLResponse)
async def display_numberlottery(request: Request, game_id: str):
    return numberlottery_renderer().TemplateResponse(
        "numberlottery/numberlottery.html",
        {
            "game_id": game_id,
            "request": request,
        },
    )
