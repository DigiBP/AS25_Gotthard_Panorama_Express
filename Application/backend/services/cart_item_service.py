from datetime import date, timedelta
from typing import List

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.models.cart import Cart
from Application.backend.models.cart_item import AddToCartRequest, CartItem
from Application.backend.models.inventory import Inventory
from Application.backend.models.medication import Medication


async def get_all_cart_items(session: AsyncSession) -> List[CartItem]:
    result = await session.exec(select(CartItem))
    return result.all()


async def get_expiring_items(session: AsyncSession, days: int = 7) -> List[CartItem]:
    today = date.today()
    cutoff = today + timedelta(days=days)
    result = await session.exec(
        select(CartItem)
        .where(CartItem.expiration_date != None)
        .where(CartItem.expiration_date <= cutoff)
    )
    return result.all()


async def get_cart_contents(session: AsyncSession, cart_id: int) -> List[CartItem]:
    result = await session.exec(select(CartItem).where(CartItem.cart_id == cart_id))
    return result.all()


async def add_medication_to_cart(
    session: AsyncSession, request: AddToCartRequest
) -> CartItem:
    cart = await session.get(Cart, request.cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    medication = await session.get(Medication, request.medication_id)
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")

    inventory = await session.get(Inventory, request.inventory_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    if inventory.amount < request.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough inventory for {medication.name}. Available: {inventory.amount} {inventory.unit}",
        )

    inventory.amount -= request.amount
    session.add(inventory)

    unit = inventory.unit
    expiration_date = inventory.expirationDate

    cart_item = CartItem(
        cart_id=request.cart_id,
        inventory_id=request.inventory_id,
        medication_id=request.medication_id,
        amount=request.amount,
        unit=unit,
        time_sensitive=request.time_sensitive,
        expiration_date=expiration_date,
    )

    session.add(cart_item)
    await session.commit()
    await session.refresh(cart_item)

    return cart_item


async def remove_cart_item(session: AsyncSession, id: int) -> None:
    cart_item = await session.get(CartItem, id)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    # Return the amount back to inventory
    inventory = await session.get(Inventory, cart_item.inventory_id)
    if inventory:
        inventory.amount += cart_item.amount
        session.add(inventory)

    await session.delete(cart_item)
    await session.commit()
