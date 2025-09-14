from datetime import datetime, timezone

from lnbits.db import Database
from lnbits.helpers import urlsafe_short_hash

from .models import Game, Player

db = Database("ext_numbers")

###### GAMES ######


async def create_game(data: Game) -> Game:
    data.id = urlsafe_short_hash()
    game = Game(**data.dict())
    await db.insert("numbers.games", game)
    return game


async def update_game(game: Game) -> Game:
    await db.update("numbers.games", game)
    return game


async def get_game(game_id: str) -> Game:
    return await db.fetchone(
        "SELECT * FROM numbers.games WHERE id = :id",
        {"id": game_id},
        Game,
    )


async def get_games_by_user(user: str) -> list[Game]:
    return await db.fetchall(
        "SELECT * FROM numbers.games WHERE user_id = :user_id",
        {"user_id": user},
        Game,
    )


async def get_all_pending_games() -> list[Game]:
    query = (
        "SELECT * FROM numbers.games "
        "WHERE completed = :completed "
        "AND closing_date < :closing_date"
    )
    params = {
        "completed": False,
        "closing_date": datetime.now(timezone.utc),
    }
    return await db.fetchall(query, params, Game)


async def delete_game(game_id: str) -> None:
    await db.execute("DELETE FROM numbers.games WHERE id = :id", {"id": game_id})


###### PLAYERS ######


async def create_player(data: Player) -> Player:
    data.id = urlsafe_short_hash()
    player = Player(**data.dict())
    await db.insert("numbers.players", player)
    return player


async def update_player(player: Player) -> Player:
    await db.update("numbers.players", player)
    return player


async def get_all_players(game_id: str) -> list[Player]:
    return await db.fetchall(
        "SELECT * FROM numbers.players WHERE game_id = :game_id",
        {"game_id": game_id},
        Player,
    )


async def get_all_unpaid_players(game_id: str) -> list[Player]:
    return await db.fetchall(
        "SELECT * FROM numbers.players WHERE game_id = :game_id AND paid = :paid",
        {"game_id": game_id, "paid": False},
        Player,
    )


async def get_all_unpaid_players_with_winning_number(
    game_id: str, height_number: int
) -> list[Player]:
    query = (
        "SELECT * FROM numbers.players "
        "WHERE game_id = :game_id "
        "AND height_number = :height_number "
        "AND paid = :paid"
    )
    params = {"game_id": game_id, "height_number": height_number, "paid": False}
    return await db.fetchall(query, params, Player)


async def delete_players(game_id: str) -> None:
    await db.execute(
        "DELETE FROM numbers.players WHERE game_id = :game_id",
        {"game_id": game_id},
    )
