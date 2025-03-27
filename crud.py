from typing import List

from lnbits.db import Database
from lnbits.helpers import urlsafe_short_hash

from .models import CreateNumbers, Numbers, Player

db = Database("ext_numbers")

###### GAMES ######

async def create_numbers(data: CreateNumbers, wallet, user) -> List[Numbers]:
    numbers = Numbers(**data.dict(), id=urlsafe_short_hash(), wallet=wallet, user=user)
    await db.insert("numbers.numbers", numbers)
    return await get_numbers(user)


async def update_numbers(numbers: Numbers) -> Numbers:
    await db.update("numbers.numbers", numbers)
    return numbers


async def get_numbers(numbers_id: str) -> Numbers:
    return await db.fetchone(
        "SELECT * FROM numbers.numbers WHERE id = :id",
        {"id": numbers_id},
        Numbers,
    )


async def get_numbers_by_user(user: str) -> List[Numbers]:
    return await db.fetchall(
        "SELECT * FROM numbers.numbers WHERE user = :user",
        {"user": user},
        Numbers,
    )


async def get_all_pending_numbers() -> List[Numbers]:
    return await db.fetchall(
        "SELECT * FROM numbers.numbers WHERE completed = :completed",
        {"completed": 0},
        Numbers,
    )

###### PLAYERS ######

async def create_player(data: Player) -> Player:
    player = Player(**data.dict(), id=urlsafe_short_hash())
    await db.insert("numbers.players", player)
    return player

async def update_player(player: Player) -> Player:
    await db.update("numbers.players", player)
    return player

async def get_all_numbers_players(numbers_id: str, height_number: int) -> List[Player]:
    return await db.fetchall(
        "SELECT * FROM numbers.players WHERE numbers_id = :numbers_id AND height_number = :height_number AND paid = :paid",
        {"numbers_id": numbers_id, "height_number": height_number, "paid": False},
        Player,
    )

async def get_all_unpaid_players(numbers_ids: List[str]) -> List[Player]:
    placeholders = ", ".join([f":id_{i}" for i in range(len(numbers_ids))])
    query = f"""
        SELECT * FROM numbers.players
        WHERE numbers_id IN ({placeholders})
        AND paid = false
        AND owed > 0
    """
    params = {f"id_{i}": numbers_ids[i] for i in range(len(numbers_ids))}
    return await db.fetchall(query, params, Player)

async def delete_numbers(numbers_id: str) -> None:
    await db.execute("DELETE FROM numbers.numbers WHERE id = :id", {"id": numbers_id})
