from typing import List

from lnbits.db import Database
from lnbits.helpers import urlsafe_short_hash
from datetime import datetime
from .models import Game, Player

db = Database("ext_numbers")

###### GAMES ######

async def create_game(data: Game) -> List[Game]:
    data.id=urlsafe_short_hash()
    game = Game(**data.dict())
    await db.insert("numbers.games", game)
    return await get_game(game.id)


async def update_game(game: Game) -> Game:
    await db.update("numbers.games", game)
    return game

async def get_game(game_id: str) -> Game:
    return await db.fetchone(
        "SELECT * FROM numbers.games WHERE id = :id",
        {"id": game_id},
        Game,
    )

async def get_games_by_user(user: str) -> List[Game]:
    return await db.fetchall(
        "SELECT * FROM numbers.games WHERE user = :user",
        {"user": user},
        Game,
    )

async def get_all_pending_games() -> List[Game]:
    return await db.fetchall(
        "SELECT * FROM numbers.games WHERE completed = :completed AND closing_date < :closing_date",
        {"completed": 0, "closing_date": datetime.now()},
        Game,
    )

###### PLAYERS ######

async def create_player(data: Player) -> Player:
    player = Player(**data.dict(), id=urlsafe_short_hash())
    await db.insert("numbers.players", player)
    return player

async def update_player(player: Player) -> Player:
    await db.update("numbers.players", player)
    return player

async def get_all_game_players(game_id: str, height_number: int) -> List[Player]:
    return await db.fetchall(
        "SELECT * FROM numbers.players WHERE game_id = :game_id AND height_number = :height_number AND paid = :paid",
        {"game_id": game_id, "height_number": height_number, "paid": False},
        Player,
    )

async def get_all_unpaid_players(game_ids: List[str]) -> List[Player]:
    placeholders = ", ".join([f":id_{i}" for i in range(len(game_ids))])
    query = f"""
        SELECT * FROM numbers.players
        WHERE game_id IN ({placeholders})
        AND paid = false
        AND owed > 0
    """
    params = {f"id_{i}": game_ids[i] for i in range(len(game_ids))}
    return await db.fetchall(query, params, Player)

async def delete_game(game_id: str) -> None:
    await db.execute("DELETE FROM numbers.games WHERE id = :id", {"id": game_id})
