from datetime import datetime, timezone

from fastapi import Query
from pydantic import BaseModel


class Game(BaseModel):
    id: str | None = None
    wallet: str | None = None
    user: str | None = None
    name: str | None = None
    closing_date: datetime
    buy_in_max: int = 0
    haircut: int = 0
    odds: int = 0
    completed: bool = False
    block_height: str = ""
    mempool: str = "https://mempool.space"
    height_number: int = 0
    created_at: datetime = datetime.now(timezone.utc)

    class Config:
        extra = "allow"


class PublicGame(BaseModel):
    name: str | None = None
    closing_date: datetime
    buy_in_max: int = 0
    haircut: int = 0
    odds: int = 0
    completed: bool = False
    block_height: str = ""
    height_number: int = 0


class Player(BaseModel):
    id: str | None = None
    game_id: str = Query(None)
    height_number: int = 0
    buy_in: int = 0
    ln_address: str = Query(None)
    paid: bool = False
    owed: int = 0
    created_at: datetime = datetime.now(timezone.utc)
