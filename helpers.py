from datetime import datetime, timezone

import httpx
from lnbits.core.services import get_pr_from_lnurl, pay_invoice

from .crud import (
    get_all_unpaid_players,
    get_all_unpaid_players_with_winning_number,
    update_game,
    update_player,
)


async def get_latest_block(mempool: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{mempool}/api/blocks")
        assert response.status_code == 200
        return response.json()[0]
    return None


def get_game_winner(block_hash: str, odds: int) -> int:
    tail_hex = block_hash[-6:]
    tail_decimal = int(tail_hex, 16)
    return tail_decimal % odds


async def calculate_winners(game):
    if game.completed:
        return
    if datetime.now().timestamp() < game.closing_date.timestamp():
        return
    players = await get_all_unpaid_players(game.id)
    if not players:
        game.completed = True
        await update_game(game)
        return
    block = await get_latest_block(game.mempool)
    if not block:
        return
    # buffer to stop cheating
    if datetime.now(timezone.utc).timestamp() > game.closing_date.timestamp():
        pass
    elif (
        block["timestamp"] > game.closing_date.timestamp()
        or datetime.now(timezone.utc).timestamp() - block["timestamp"] > 25 * 60
    ):
        return
    # get the winning number
    game.block_height = block["id"]
    game.height_number = get_game_winner(block["id"], game.odds)
    winning_players = await get_all_unpaid_players_with_winning_number(
        game.id, game.height_number
    )
    # pay all the winning players
    for player in winning_players:
        max_sat = (player.buy_in * game.odds) - (player.buy_in * game.odds) * (
            game.haircut / 100
        )
        pr = await get_pr_from_lnurl(player.ln_address, int(max_sat * 1000))
        try:
            await pay_invoice(
                wallet_id=game.wallet,
                payment_request=pr,
                max_sat=max_sat,
                description=f"({player.ln_address}) won the numbers {game.name}!",
            )
            player.paid = True
            await update_player(player)
        except Exception:
            # if fails, player is owed and paid manually by admin
            player.paid = False
            player.owed = max_sat
            await update_player(player)
    game.completed = True
    await update_game(game)
    return
