from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer
from loguru import logger
from .crud import get_game

numbers_generic_router: APIRouter = APIRouter()


def numbers_renderer():
    return template_renderer(["numbers/templates"])


@numbers_generic_router.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return numbers_renderer().TemplateResponse(
        "numbers/index.html", {"request": request, "user": user.json()}
    )


@numbers_generic_router.get("/{game_id}", response_class=HTMLResponse)
async def display_numbers(request: Request, game_id: str):
    game = await get_game(game_id)
    logger.debug(game)
    return numbers_renderer().TemplateResponse(
        "numbers/numbers.html",
        {
            "game_id": game_id,
            "completed": game.completed,
            "height_number": game.height_number,
            "block_height": game.block_height,
            "odds": game.odds,
            "request": request,
        },
    )
