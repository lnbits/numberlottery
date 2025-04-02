from datetime import datetime, timezone
from typing import Optional

from fastapi import Query
from pydantic import BaseModel


class Game(BaseModel):
    id: Optional[str] = None
    wallet: Optional[str] = None
    user: Optional[str] = None
    name: Optional[str] = None
    closing_date: datetime
    buy_in_max: int = 0
    haircut: int = 0
    odds: int = 0
    completed: bool = False
    block_height: str = ""
    height_number: int = 0
    created_at: datetime = datetime.now(timezone.utc)

    class Config:
        extra = "allow"


class Player(BaseModel):
    id: Optional[str] = None
    game_id: str = Query(None)
    height_number: int = 0
    buy_in: int = 0
    ln_address: str = Query(None)
    paid: bool = False
    owed: int = 0
    created_at: datetime = datetime.now(timezone.utc)
