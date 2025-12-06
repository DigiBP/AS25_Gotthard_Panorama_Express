from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date
from enum import Enum


class CartStatus(str, Enum):
    prepared = "Prepared"
    in_use = "In-Use"
    closed = "Closed"

class Cart(SQLModel, table=True):
    __tablename__ = "carts"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    status: CartStatus
    patientId: str
    operation: str
    operationDate: date
    anaesthesiaType: str
    roomNumber: str


class CartCreate(SQLModel):
    status: CartStatus
    patientId: str
    operation: str
    operationDate: date
    anaesthesiaType: str
    roomNumber: str


CART_EXAMPLE = {
    "status": "Prepared",
    "patientId": "patient-123",
    "operation": "Dekompression",
    "operationDate": "2025-12-05",
    "anaesthesiaType": "General",
    "roomNumber": "OR-3"
}