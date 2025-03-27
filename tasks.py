import asyncio
import random

from lnbits.core.models import Payment
from lnbits.tasks import register_invoice_listener
from loguru import logger
from .models import Player
from .crud import (
    get_all_pending_numbers,
    get_numbers,
    create_player,
)
from .helpers import calculate_winners


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
            numbers = await get_all_pending_numbers()
            for numbers in numbers:
                logger.error("Found pending numbers, calculating winner")
                await calculate_winners(numbers)
        except Exception as ex:
            logger.error(ex)

        minute_counter += 1
        await asyncio.sleep(60 + random.randint(-3, 3))  # to avoid herd effect


async def on_invoice_paid(payment: Payment) -> None:
    if payment.extra.get("tag") == "numbers":
        ln_address = payment.extra["ln_address"]
        numbers_id = payment.extra["numbers_id"]
        height_number = payment.extra["height_number"]
        # fetch details
        numbers = await get_numbers(numbers_id)
        if not numbers:
            return
        # add player
        player = Player(numbers_id=numbers_id, ln_address=ln_address, height_number=height_number, buy_in=payment.amount_msat)
        await create_player(player)
