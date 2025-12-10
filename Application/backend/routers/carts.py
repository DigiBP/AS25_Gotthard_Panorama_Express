from typing import List

from fastapi import APIRouter, Body, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.core.database import get_session
from Application.backend.models.cart import CART_EXAMPLE, Cart, CartCreate, CartStatus
from Application.backend.services.cart_service import (
    add_cart,
    get_all_carts,
    update_cart_status,
)

router = APIRouter(prefix="/carts", tags=["Carts"])


@router.get("/", response_model=List[Cart])
async def list_carts(session: AsyncSession = Depends(get_session)):
    return await get_all_carts(session)


@router.post("/", response_model=Cart)
async def create_cart(
    cart: CartCreate = Body(..., example=CART_EXAMPLE),
    session: AsyncSession = Depends(get_session),
):
    return await add_cart(session, cart)


@router.patch("/{cart_id}/status", response_model=Cart)
async def change_cart_status(
    cart_id: int,
    new_status: CartStatus = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
):
    return await update_cart_status(session, cart_id, new_status)


@router.delete("/{cart_id}")
async def delete_cart(
    cart_id: int,
    session: AsyncSession = Depends(get_session),
):
    from Application.backend.services.cart_service import remove_cart

    await remove_cart(session, cart_id)
    return {"message": "Cart deleted successfully"}
