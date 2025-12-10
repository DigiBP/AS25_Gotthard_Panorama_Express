from fastapi import APIRouter, Depends, Body
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List

from Application.backend.core.database import get_session
from Application.backend.models.order import Order, OrderCreate, ORDER_EXAMPLE
from Application.backend.services.order_service import get_all_orders, add_order, delete_order

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/", response_model=List[Order])
async def list_orders(session: AsyncSession = Depends(get_session)):
    return await get_all_orders(session)


@router.post("/", response_model=Order)
async def add_order_item(order: OrderCreate = Body(..., example=ORDER_EXAMPLE), session: AsyncSession = Depends(get_session)):
    new_order = await add_order(session, order)
    return new_order


@router.delete("/{order_id}")
async def remove_order(order_id: int, session: AsyncSession = Depends(get_session)):
    await delete_order(session, order_id)
    return {"detail": f"Order '{order_id}' deleted successfully"}