from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date


class Inventory(SQLModel, table=True):
    __tablename__ = "inventory"

    id: Optional[int] = Field(default=None, primary_key=True)
    medicationId: str = Field(foreign_key="medications.medicationId", index=True)
    batchNumber: str # Unique?
    amount: float
    unit: str
    location: str
    expirationDate: date
    min_stock: float


class InventoryCreate(SQLModel):
    medicationId: str
    batchNumber: str
    amount: float
    unit: str
    location: str
    expirationDate: date
    min_stock: Optional[float] = None


INVENTORY_POST_EXAMPLE = {
    "medicationId": "relaxant-001",
    "batchNumber": "B001",
    "amount": 42,
    "unit": "mg",
    "location": "A1",
    "expirationDate": "2025-12-31",
    "min_stock": 10
}