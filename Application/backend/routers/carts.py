from fastapi import APIRouter, Depends, Body
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List

from Application.backend.core.database import get_session
from Application.backend.models.cart import Cart, CartCreate, CartStatus, CART_EXAMPLE
from Application.backend.services.cart_service import get_all_carts, add_cart, update_cart_status

router = APIRouter(prefix="/carts", tags=["Carts"])

@router.get("/", response_model=List[Cart])
async def list_carts(session: AsyncSession = Depends(get_session)):
    return await get_all_carts(session)


@router.post("/", response_model=Cart)
async def create_cart(cart: CartCreate = Body(..., example=CART_EXAMPLE), session: AsyncSession = Depends(get_session)):
    return await add_cart(session, cart)


@router.patch("/{cart_id}/status", response_model=Cart)
async def change_cart_status(
    cart_id: int,
    new_status: CartStatus = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
):
    return await update_cart_status(session, cart_id, new_status)
