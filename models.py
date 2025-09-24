from datetime import datetime, timezone

from fastapi import Query
from pydantic import BaseModel, validator


class Game(BaseModel):
    id: str | None = None
    wallet: str | None = None
    user_id: str | None = None
    name: str | None = None
    closing_date: datetime
    buy_in_max: int = 0
    haircut: int = 0
    odds: int = 0
    completed: bool = False
    block_hash: str = ""
    mempool: str = "https://mempool.space"
    block_number: int = 0
    created_at: datetime = datetime.now(timezone.utc)

    class Config:
        extra = "allow"

    @validator("closing_date", pre=True, always=True)
    def force_utc(cls, v):
        if isinstance(v, datetime):
            return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        return datetime.fromtimestamp(int(v), tz=timezone.utc)

class PublicGame(BaseModel):
    name: str | None = None
    closing_date: datetime
    buy_in_max: int = 0
    haircut: int = 0
    odds: int = 0
    completed: bool = False
    block_hash: str = ""
    block_number: int = 0

    @validator("closing_date", pre=True, always=True)
    def force_utc(cls, v):
        if isinstance(v, datetime):
            return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        return datetime.fromtimestamp(int(v), tz=timezone.utc)

class Player(BaseModel):
    id: str | None = None
    game_id: str = Query(None)
    block_number: int = 0
    buy_in: int = 0
    ln_address: str = Query(None)
    paid: bool = False
    owed: int = 0
    created_at: datetime = datetime.now(timezone.utc)
