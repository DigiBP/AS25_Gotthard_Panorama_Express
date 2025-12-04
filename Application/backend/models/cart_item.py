from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date


class CartItem(SQLModel, table=True):
    __tablename__ = "cart_items"

    id: Optional[int] = Field(default=None, primary_key=True)

    cart_id: int = Field(foreign_key="carts.id")
    inventory_id: int = Field(foreign_key="inventory.id")

    # Now correctly points to Medication.medicationId
    medication_id: str = Field(foreign_key="medications.medicationId")

    time_sensitive: bool
    amount: float
    unit: str
    expiration_date: Optional[date] = None


class AddToCartRequest(SQLModel):
    cart_id: int
    inventory_id: int
    medication_id: str
    amount: float
    time_sensitive: bool = False


CART_ITEM_EXAMPLE = {
    "cart_id": 1,
    "inventory_id": 1,
    "medication_id": "relaxant-001",
    "amount": 2.0,
    "time_sensitive": True,
}