from typing import List, Optional

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.models.cart import Cart, CartCreate, CartStatus


async def get_all_carts(session: AsyncSession) -> List[Cart]:
    result = await session.exec(select(Cart))
    return result.all()


async def get_cart_by_id(session: AsyncSession, cart_id: str) -> Optional[Cart]:
    result = await session.exec(select(Cart).where(Cart.id == cart_id))
    return result.one_or_none()


async def add_cart(session: AsyncSession, cart_data: CartCreate):
    cart_item = Cart(**cart_data.model_dump())
    session.add(cart_item)
    await session.commit()
    await session.refresh(cart_item)
    return cart_item


async def update_cart_status(session: AsyncSession, cart_id: str, new_status: CartStatus) -> Cart:
    cart_item = await get_cart_by_id(session, cart_id)
    if not cart_item:
        raise HTTPException(status_code=404, detail=f"Cart '{cart_id}' not found")
    cart_item.status = new_status
    session.add(cart_item)
    await session.commit()
    await session.refresh(cart_item)
    return cart_item