from fastapi import APIRouter, Depends, Body
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List

from Application.backend.core.database import get_session
from Application.backend.models.order import Order, OrderCreate, ORDER_EXAMPLE
from Application.backend.services.order_service import get_all_orders, add_order, delete_order

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/", response_model=List[Order], summary="List all orders")
async def list_orders(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all orders in the system.

    - **session**: Async database session (automatically injected).

    Returns a list of `Order` objects.
    """
    return await get_all_orders(session)


@router.post("/", response_model=Order, summary="Create a new order")
async def add_order_item(
    order: OrderCreate = Body(
        ...,
        example=ORDER_EXAMPLE,
        description="Order data to create a new order"
    ),
    session: AsyncSession = Depends(get_session)
):
    """
    Add a new order to the system.

    - **order**: Order data to register.
    - **session**: Async database session (automatically injected).

    Returns the created `Order` object.
    """
    new_order = await add_order(session, order)
    return new_order


@router.delete("/{order_id}", summary="Delete an order")
async def remove_order(
    order_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete an existing order by its ID.

    - **order_id**: ID of the order to delete.
    - **session**: Async database session (automatically injected).

    Returns a confirmation message.
    """
    await delete_order(session, order_id)
    return {"detail": f"Order '{order_id}' deleted successfully"}