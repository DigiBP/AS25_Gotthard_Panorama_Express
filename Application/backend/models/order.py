from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from typing import Optional, List, Dict
from datetime import date

class Order(SQLModel, table=True):
    __tablename__ = "orders"

    # Auto-Increment ID
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str
    date: date
    medications: List[Dict] = Field(sa_column=Column(JSON))
    isInternal: bool
    isRush: bool


class OrderCreate(SQLModel):
    name: str
    date: date
    medications: List[Dict]
    isInternal: bool
    isRush: bool


ORDER_EXAMPLE = {
    "name": "Weekly Restock",
    "date": "2025-12-01",
    "medications": [
    {"medicationId": "relaxant-001", "amount": 50},
    {"medicationId": "relaxant-002", "amount": 20}
    ],
    "isInternal": False,
    "isRush": True
}