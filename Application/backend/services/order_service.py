from typing import List, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import HTTPException

from Application.backend.models.order import Order, OrderCreate


async def get_all_orders(session: AsyncSession) -> List[Order]:
    result = await session.exec(select(Order))
    return result.all()


async def get_order_by_id(session: AsyncSession, order_id: str) -> Optional[Order]:
    result = await session.exec(select(Order).where(Order.id == order_id))
    return result.one_or_none()


async def add_order(session: AsyncSession, order_data: OrderCreate) -> Order:
    order_item = Order(**order_data.model_dump())  # ID bleibt None → DB setzt sie automatisch
    session.add(order_item)
    await session.commit()
    await session.refresh(order_item)
    return order_item


async def delete_order(session: AsyncSession, order_id: str) -> None:
    order_item = await get_order_by_id(session, order_id)
    if not order_item:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
    await session.delete(order_item)
    await session.commit()