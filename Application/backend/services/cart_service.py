from typing import List, Optional

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.models.cart import Cart, CartCreate, CartStatus
from Application.backend.models.inventory import Inventory


async def get_all_carts(session: AsyncSession) -> List[Cart]:
    """
    Retrieve all carts from the database.

    - **session**: Async database session.

    Returns a list of all `Cart` objects.
    """
    result = await session.exec(select(Cart))
    return result.all()


async def get_cart_by_id(session: AsyncSession, cart_id: str) -> Optional[Cart]:
    """
    Retrieve a cart by its ID.

    - **session**: Async database session.
    - **cart_id**: ID of the cart to retrieve.

    Returns the `Cart` object if found, otherwise `None`.
    """
    result = await session.exec(select(Cart).where(Cart.id == cart_id))
    return result.one_or_none()


async def add_cart(session: AsyncSession, cart_data: CartCreate) -> Cart:
    """
    Add a new cart to the database.

    - **session**: Async database session.
    - **cart_data**: `CartCreate` object containing cart details.

    Returns the newly created `Cart` object.
    """
    cart_item = Cart(**cart_data.model_dump())
    session.add(cart_item)
    await session.commit()
    await session.refresh(cart_item)
    return cart_item


async def update_cart_status(
    session: AsyncSession, cart_id: str, new_status: CartStatus
) -> Cart:
    """
    Update the status of a cart.

    - **session**: Async database session.
    - **cart_id**: ID of the cart to update.
    - **new_status**: New `CartStatus` value (prepared, in_use, closed).

    Returns the updated `Cart` object.

    Raises:
        HTTPException 404 if the cart does not exist.
    """
    cart_item = await get_cart_by_id(session, cart_id)
    if not cart_item:
        raise HTTPException(status_code=404, detail=f"Cart '{cart_id}' not found")
    cart_item.status = new_status
    session.add(cart_item)
    await session.commit()
    await session.refresh(cart_item)
    return cart_item


async def remove_cart(session: AsyncSession, cart_id: int) -> None:
    """
    Remove a cart and return all associated items to inventory.

    - **session**: Async database session.
    - **cart_id**: ID of the cart to delete.

    Adjusts inventory amounts for all `CartItem`s in the cart and deletes them,
    then deletes the cart itself.

    Raises:
        HTTPException 404 if the cart does not exist.
    """
    from Application.backend.models.cart_item import CartItem

    cart = await session.get(Cart, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    result = await session.exec(select(CartItem).where(CartItem.cart_id == cart_id))
    cart_items = result.all()

    for item in cart_items:
        inventory = await session.get(Inventory, item.inventory_id)
        if inventory:
            inventory.amount += item.amount
            session.add(inventory)
        await session.delete(item)

    await session.delete(cart)
    await session.commit()