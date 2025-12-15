from typing import List, Optional

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.models.order import Order, OrderCreate


async def get_all_orders(session: AsyncSession) -> List[Order]:
    """
    Retrieve all orders.

    - **session**: Async database session.

    Returns a list of all `Order` entries.
    """
    result = await session.exec(select(Order))
    return result.all()


async def get_order_by_id(session: AsyncSession, order_id: str) -> Optional[Order]:
    """
    Retrieve a single order by its ID.

    - **session**: Async database session.
    - **order_id**: ID of the order.

    Returns the `Order` if found, otherwise `None`.
    """
    result = await session.exec(select(Order).where(Order.id == order_id))
    return result.one_or_none()


async def add_order(session: AsyncSession, order_data: OrderCreate) -> Order:
    """
    Create a new order.

    - **session**: Async database session.
    - **order_data**: Data required to create the order.

    Returns the newly created `Order` object.
    """
    order_item = Order(**order_data.model_dump())
    session.add(order_item)
    await session.commit()
    await session.refresh(order_item)
    return order_item


async def delete_order(session: AsyncSession, order_id: str) -> None:
    """
    Delete an order by its ID.

    - **session**: Async database session.
    - **order_id**: ID of the order.

    Raises:
        HTTPException 404 if the order does not exist.
    """
    order_item = await get_order_by_id(session, order_id)
    if not order_item:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
    await session.delete(order_item)
    await session.commit()