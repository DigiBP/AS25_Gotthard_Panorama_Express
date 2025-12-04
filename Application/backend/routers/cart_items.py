from typing import List

from fastapi import APIRouter, Depends, Body
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.core.database import get_session
from Application.backend.models.cart_item import CartItem, AddToCartRequest, CART_ITEM_EXAMPLE
from Application.backend.services.cart_item_service import get_expiring_items, get_cart_contents, add_medication_to_cart

router = APIRouter(prefix="/cart-items", tags=["Cart Items"])


@router.get("/expiring", response_model=List[CartItem])
async def list_expiring_items(session: AsyncSession = Depends(get_session)):
    return await get_expiring_items(session)


@router.get("/cart/{cart_id}", response_model=List[CartItem])
async def list_cart_contents(cart_id: int, session: AsyncSession = Depends(get_session)):
    return await get_cart_contents(session, cart_id)


@router.post("/add", response_model=CartItem)
async def add_to_cart(
    request: AddToCartRequest = Body(..., example=CART_ITEM_EXAMPLE),
    session: AsyncSession = Depends(get_session)
):
    return await add_medication_to_cart(session, request)