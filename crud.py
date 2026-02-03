from time import time

from lnbits.db import Database
from lnbits.helpers import urlsafe_short_hash

from .models import Game, Player

db = Database("ext_numberlottery")

###### GAMES ######


async def create_game(data: Game) -> Game:
    data.id = urlsafe_short_hash()
    game = Game(**data.dict())
    await db.insert("numberlottery.games", game)
    return game


async def update_game(game: Game) -> Game:
    await db.update("numberlottery.games", game)
    return game


async def get_game(game_id: str) -> Game:
    return await db.fetchone(
        "SELECT * FROM numberlottery.games WHERE id = :id",
        {"id": game_id},
        Game,
    )


async def get_games_by_user(user: str) -> list[Game]:
    return await db.fetchall(
        "SELECT * FROM numberlottery.games WHERE user_id = :user_id",
        {"user_id": user},
        Game,
    )


async def get_all_pending_games() -> list[Game]:
    return await db.fetchall(
        f"""
        SELECT * FROM numberlottery.games WHERE completed = :c
        AND closing_date < {db.timestamp_placeholder('now')}
        """,
        {"c": False, "now": time()},
        Game,
    )


async def delete_game(game_id: str) -> None:
    await db.execute("DELETE FROM numberlottery.games WHERE id = :id", {"id": game_id})


###### PLAYERS ######


async def create_player(data: Player) -> Player:
    data.id = urlsafe_short_hash()
    player = Player(**data.dict())
    await db.insert("numberlottery.players", player)
    return player


async def update_player(player: Player) -> Player:
    await db.update("numberlottery.players", player)
    return player


async def get_all_players(game_id: str) -> list[Player]:
    return await db.fetchall(
        "SELECT * FROM numberlottery.players WHERE game_id = :game_id",
        {"game_id": game_id},
        Player,
    )


async def get_all_unpaid_players(game_id: str) -> list[Player]:
    return await db.fetchall(
        "SELECT * FROM numberlottery.players WHERE game_id = :game_id AND paid = :paid",
        {"game_id": game_id, "paid": False},
        Player,
    )


async def get_all_unpaid_players_with_winning_number(
    game_id: str, block_number: int
) -> list[Player]:
    query = (
        "SELECT * FROM numberlottery.players "
        "WHERE game_id = :game_id "
        "AND block_number = :block_number "
        "AND paid = :paid"
    )
    params = {"game_id": game_id, "block_number": block_number, "paid": False}
    return await db.fetchall(query, params, Player)


async def delete_players(game_id: str) -> None:
    await db.execute(
        "DELETE FROM numberlottery.players WHERE game_id = :game_id",
        {"game_id": game_id},
    )
