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
    """
    Retrieve all cart items in the database.

    - **session**: Async database session (injected via Depends).

    Returns a list of all `CartItem` objects.
    """
    result = await session.exec(select(CartItem))
    return result.all()


async def get_expiring_items(session: AsyncSession, days: int = 7) -> List[CartItem]:
    """
    Retrieve cart items that will expire within a given number of days.

    - **session**: Async database session.
    - **days**: Number of days from today to check for expiration (default: 7).

    Returns a list of `CartItem` objects with `expiration_date` within the specified window.
    """
    today = date.today()
    cutoff = today + timedelta(days=days)
    result = await session.exec(
        select(CartItem)
        .where(CartItem.expiration_date != None)
        .where(CartItem.expiration_date <= cutoff)
    )
    return result.all()


async def get_cart_contents(session: AsyncSession, cart_id: int) -> List[CartItem]:
    """
    Retrieve all items in a specific cart.

    - **session**: Async database session.
    - **cart_id**: ID of the cart to retrieve contents from.

    Returns a list of `CartItem` objects belonging to the specified cart.
    """
    result = await session.exec(select(CartItem).where(CartItem.cart_id == cart_id))
    return result.all()


async def add_medication_to_cart(
    session: AsyncSession, request: AddToCartRequest
) -> CartItem:
    """
    Add a medication to a cart.

    - **session**: Async database session.
    - **request**: `AddToCartRequest` containing cart_id, inventory_id, medication_id, amount, and time_sensitive flag.

    Checks for existence of cart, medication, and inventory, validates inventory amount,
    decrements inventory, creates a CartItem, and commits changes.

    Returns the newly created `CartItem`.

    Raises:
        HTTPException 404 if cart, medication, or inventory is not found.
        HTTPException 400 if requested amount exceeds inventory.
    """
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

    cart_item = CartItem(
        cart_id=request.cart_id,
        inventory_id=request.inventory_id,
        medication_id=request.medication_id,
        amount=request.amount,
        unit=inventory.unit,
        time_sensitive=request.time_sensitive,
        expiration_date=inventory.expirationDate,
    )

    session.add(cart_item)
    await session.commit()
    await session.refresh(cart_item)

    return cart_item


async def remove_cart_item(session: AsyncSession, id: int) -> None:
    """
    Remove a cart item and return its quantity to inventory.

    - **session**: Async database session.
    - **id**: ID of the cart item to remove.

    Adjusts the inventory amount accordingly and deletes the cart item from the database.

    Raises:
        HTTPException 404 if the cart item does not exist.
    """
    cart_item = await session.get(CartItem, id)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    inventory = await session.get(Inventory, cart_item.inventory_id)
    if inventory:
        inventory.amount += cart_item.amount
        session.add(inventory)

    await session.delete(cart_item)
    await session.commit()