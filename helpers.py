import random
from datetime import datetime

import httpx
from lnbits.core.services import pay_invoice
from lnbits.core.views.api import api_lnurlscan

from .crud import (
    update_numbers,
    get_all_numbers_players
)
import requests
from datetime import datetime, timezone

async def get_pr(ln_address, amount):
    data = await api_lnurlscan(ln_address)
    if data.get("status") == "ERROR":
        return
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url=f"{data['callback']}?amount={amount* 1000}")
            if response.status_code != 200:
                return
            return response.json()["pr"]
    except Exception:
        return None

def get_block_after_now():
    now = datetime.now(timezone.utc)
    blocks = requests.get("https://mempool.space/api/blocks").json()
    for block in blocks:
        block_time = datetime.fromtimestamp(block["timestamp"], tz=timezone.utc)
        if block_time > now:
            return block
    return None

def get_numbers_game_winner(block_hash: str, odds: int) -> int:
    tail_hex = block_hash[-4:]
    tail_decimal = int(tail_hex, 16)
    return tail_decimal % odds

async def calculate_winners(numbers):
    if (
        datetime.now().timestamp() > numbers.closing_date.timestamp()
        and not numbers.completed
    ):
        block = get_block_after_now()
        if not block:
            return
        numbers.block_height = block["id"]
        numbers.height_number = get_numbers_game_winner(block["id"], numbers.odds)
        players = await get_all_numbers_players(numbers.id, numbers.height_number)
        for player in players:
            max_sat = (player.buy_in * numbers.odds) * (numbers.haircut / 100)
            pr = await get_pr(player.ln_address, max_sat)
            try:
                await pay_invoice(
                    wallet_id=numbers.wallet,
                    payment_request=pr,
                    max_sat=max_sat,
                    description=f"({player.ln_address}) won the numbers {numbers.name}!",
                )
                player.paid = True
                await update_player(player)
            except Exception:
                player.paid = False
                player.owed = max_sat
                await update_player(player)
        numbers.completed = True
        await update_numbers(numbers)
    return
