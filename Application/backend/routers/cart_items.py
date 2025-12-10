from typing import List

from fastapi import APIRouter, Body, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.core.database import get_session
from Application.backend.models.cart_item import (
    CART_ITEM_EXAMPLE,
    AddToCartRequest,
    CartItem,
)
from Application.backend.services.cart_item_service import (
    add_medication_to_cart,
    get_all_cart_items,
    get_cart_contents,
    get_expiring_items,
)

router = APIRouter(prefix="/cart-items", tags=["Cart Items"])


@router.get("/", response_model=List[CartItem])
async def list_cart_items(session: AsyncSession = Depends(get_session)):
    return await get_all_cart_items(session)


@router.get("/expiring", response_model=List[CartItem])
async def list_expiring_items(session: AsyncSession = Depends(get_session)):
    return await get_expiring_items(session)


@router.get("/cart/{cart_id}", response_model=List[CartItem])
async def list_cart_contents(
    cart_id: int, session: AsyncSession = Depends(get_session)
):
    return await get_cart_contents(session, cart_id)


@router.post("/add", response_model=CartItem)
async def add_to_cart(
    request: AddToCartRequest = Body(..., example=CART_ITEM_EXAMPLE),
    session: AsyncSession = Depends(get_session),
):
    return await add_medication_to_cart(session, request)


@router.delete("/{cart_item_id}")
async def remove_from_cart(
    cart_item_id: int, session: AsyncSession = Depends(get_session)
):
    from Application.backend.services.cart_item_service import remove_cart_item

    await remove_cart_item(session, cart_item_id)
    return {"message": "Cart item removed successfully"}

