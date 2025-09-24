import asyncio
import random

from lnbits.core.models import Payment
from lnbits.tasks import register_invoice_listener
from loguru import logger

from .crud import (
    create_player,
    get_all_pending_games,
    get_game,
)
from .helpers import calculate_winners
from .models import Player


async def wait_for_paid_invoices():
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue, "ext_numbers")

    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)


async def run_by_the_minute_task():
    minute_counter = 0
    while True:
        try:
            games = await get_all_pending_games()
            logger.debug("checking numbers games that have finished...")
            for game in games:
                await calculate_winners(game)
        except Exception as ex:
            logger.error(ex)

        minute_counter += 1
        await asyncio.sleep(60 + random.randint(-3, 3))  # to avoid herd effect


async def on_invoice_paid(payment: Payment) -> None:
    if payment.extra.get("tag") == "numbers":
        ln_address = payment.extra["ln_address"]
        game_id = payment.extra["game_id"]
        block_number = payment.extra["block_number"]
        # fetch details
        game = await get_game(game_id)
        if not game:
            return
        # add player
        player = Player(
            game_id=game_id,
            ln_address=ln_address,
            block_number=block_number,
            buy_in=int(payment.amount / 1000),
        )
        await create_player(player)
