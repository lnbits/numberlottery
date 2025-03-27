from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Query
from pydantic import BaseModel


class CreateNumbers(BaseModel):
    name: str
    haircut: int = 0
    closing_date: datetime = datetime.now(timezone.utc) + timedelta(days=1)
    odds: int = 0


class Numbers(BaseModel):
    id: Optional[str] = None
    wallet: str
    user: Optional[str] = None
    name: str
    closing_date: datetime
    buy_in_max: int = 0
    haircut: int = 0
    completed: bool = False
    block_height: str = ""
    height_number: int = 0
    created_at: datetime = datetime.now(timezone.utc)


class GetNumbersGame(BaseModel):
    id: Optional[str] = None
    name: str
    closing_date: datetime
    buy_in_max: int = 0
    haircut: int = 0
    block_height: str = ""
    height_number: int = 0
    completed: bool = False


class Player(BaseModel):
    id: Optional[str] = None
    numbers_id: str = Query(None)
    height_number: int = 0
    buy_in: int = 0
    ln_address: str = Query(None)
    paid: bool = False
    owed: int = 0
    created_at: datetime = datetime.now(timezone.utc)
