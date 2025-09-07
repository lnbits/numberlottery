from datetime import datetime
from http import HTTPStatus

from fastapi import APIRouter, Depends
from lnbits.core.crud import get_user
from lnbits.core.models import WalletTypeInfo
from lnbits.core.services import create_invoice
from lnbits.decorators import require_admin_key
from lnurl import LnurlPayResponse
from lnurl import handle as lnurl_handle
from starlette.exceptions import HTTPException

from .crud import (
    create_game,
    delete_game,
    delete_players,
    get_all_players,
    get_game,
    get_games_by_user,
)
from .models import Game, Player, PublicGame

numbers_api_router = APIRouter()

#### GAMES ####


@numbers_api_router.post("/api/v1", status_code=HTTPStatus.OK)
async def api_create_game(
    data: Game, key_info: WalletTypeInfo = Depends(require_admin_key)
):
    if data.haircut < 0 or data.haircut > 50:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Haircut must be between 0 and 50",
        )
    if data.odds > 10000000:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Odds too high: 10,000,000-1 max",
        )
    if data.closing_date.timestamp() - (30 * 60) < datetime.now().timestamp():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="To avoid cheating, games close bets 30mins before the closing"
            "date. So your game must close at least 30mins before the closing date.",
        )
    data.wallet = key_info.wallet.id
    data.user = key_info.wallet.user
    game = await create_game(data)
    if not game:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Failed to create game"
        )
    return game


@numbers_api_router.get("/api/v1/{game_id}", status_code=HTTPStatus.OK)
async def api_get_public_game(game_id: str):
    game = await get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Numbers game does not exist."
        )
    public_game = PublicGame(**game.dict())
    return public_game


@numbers_api_router.get("/api/v1")
async def api_get_games(
    key_info: WalletTypeInfo = Depends(require_admin_key),
):
    user = await get_user(key_info.wallet.user)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Failed to get user"
        )
    games = await get_games_by_user(user.id)
    return games


@numbers_api_router.delete("/api/v1/{game_id}")
async def api_delete_game(
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
    await delete_players(game_id)
    await delete_game(game_id)


#### PLAYERS ####


@numbers_api_router.post("/api/v1/join", status_code=HTTPStatus.OK)
async def api_create_player(data: Player):
    game = await get_game(data.game_id)
    if not game:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="No game found")
    if game.completed:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Game already ended"
        )
    if game.closing_date.timestamp() - (30 * 60) < datetime.now().timestamp():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Game closing within 30mins, no more bets!",
        )
    if data.buy_in > game.buy_in_max:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Buy in amount too high",
        )
    if data.height_number < 0 or data.height_number > (game.odds - 1):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Number out of range",
        )
    try:
        res = await lnurl_handle(data.ln_address)
    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=f"lnaddress error: {exc!s}"
        ) from exc
    if not isinstance(res, LnurlPayResponse):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="lnaddress return wrong response type",
        )
    try:
        assert game.wallet
        payment = await create_invoice(
            wallet_id=game.wallet,
            amount=data.buy_in,
            memo=f"Numbers {game.name} for {data.ln_address}",
            extra={
                "tag": "numbers",
                "ln_address": data.ln_address,
                "game_id": data.game_id,
                "height_number": data.height_number,
            },
        )
        return {"payment_hash": payment.payment_hash, "payment_request": payment.bolt11}
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=f"Failed to create invoice: {e}"
        ) from e


@numbers_api_router.get("/api/v1/players/{game_id}")
async def api_get_players(
    game_id: str,
    key_info: WalletTypeInfo = Depends(require_admin_key),
):
    user = await get_user(key_info.wallet.user)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Failed to get user"
        )
    game = await get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Numbers game does not exist."
        )
    if game.user != user.id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Not your game.")
    players = await get_all_players(game_id)
    return players
