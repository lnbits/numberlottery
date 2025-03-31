from datetime import datetime
from http import HTTPStatus

from fastapi import APIRouter, Depends
from lnbits.core.crud import get_user
from lnbits.core.models import WalletTypeInfo
from lnbits.core.services import create_invoice
from lnbits.decorators import require_admin_key
from loguru import logger
from starlette.exceptions import HTTPException

from .crud import (
    create_game,
    delete_game,
    get_game,
    get_games_by_user,
)
from .helpers import get_pr
from .models import Game, Player

numbers_api_router = APIRouter()


@numbers_api_router.post("/api/v1/numbers", status_code=HTTPStatus.OK)
async def api_create_numbers(
    data: Game, key_info: WalletTypeInfo = Depends(require_admin_key)
):
    if data.haircut < 0 or data.haircut > 50:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Haircut must be between 0 and 50",
        )
    data.wallet = key_info.wallet.id
    data.user = key_info.wallet.user
    game = await create_game(data)
    if not game:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Failed to create game"
        )
    return game


@numbers_api_router.get("/api/v1/numbers")
async def api_get_game(
    key_info: WalletTypeInfo = Depends(require_admin_key),
):
    user = await get_user(key_info.wallet.user)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Failed to get user"
        )
    games = await get_games_by_user(user.id)
    logger.debug(games)
    return games


@numbers_api_router.post("/api/v1/numbers/join/", status_code=HTTPStatus.OK)
async def api_join_numbers(data: Player):
    numbers_game = await get_game(data.game_id)
    logger.debug(numbers_game)
    if not numbers_game:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="No game found")
    if numbers_game.completed:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Game already ended"
        )
    pay_req = await get_pr(data.ln_address, numbers_game.buy_in)
    if not pay_req:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="lnaddress check failed"
        )
    payment = await create_invoice(
        wallet_id=numbers_game.wallet,
        amount=numbers_game.buy_in,
        memo=f"Numbers {numbers_game.name} for {data.ln_address}",
        extra={
            "tag": "numbers",
            "ln_address": data.ln_address,
            "game_id": data.game_id,
            "height_number": data.height_number,
        },
    )
    return {"payment_hash": payment.payment_hash, "payment_request": payment.bolt11}


@numbers_api_router.delete("/api/v1/numbers/{game_id}")
async def api_numbers_delete(
    game_id: str,
    key_info: WalletTypeInfo = Depends(require_admin_key),
):
    numbers = await get_game(game_id)
    if not numbers:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Pay link does not exist."
        )

    if numbers.wallet != key_info.wallet.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your pay link."
        )

    await delete_game(game_id)


@numbers_api_router.get(
    "/api/v1/numbers/{game_id}", status_code=HTTPStatus.OK
)
async def api_get_game(game_id: str):
    numbers = await get_game(game_id)
    if not numbers:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Numbers game does not exist."
        )
    if numbers.closing_date.timestamp() < datetime.now().timestamp():
        numbers.completed = True
    return Game(
        id=numbers.id,
        name=numbers.name,
        closing_date=numbers.closing_date,
        buy_in_max=numbers.buy_in_max,
        haircut=numbers.haircut,
        completed=numbers.completed,
    )
