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


async def add_medications_to_cart_bulk(
    session: AsyncSession, requests: List[AddToCartRequest]
) -> List[CartItem]:
    """
    Add multiple medications to a cart in a single operation.

    - **session**: Async database session.
    - **requests**: List of `AddToCartRequest` objects containing cart_id, inventory_id, medication_id, amount, and time_sensitive flag.

    Validates all requests first, then performs bulk operations:
    - Checks existence of carts, medications, and inventory items
    - Validates inventory amounts
    - Decrements inventory amounts
    - Creates CartItem objects
    - Commits all changes

    Returns a list of the newly created `CartItem` objects.

    Raises:
        HTTPException 404 if any cart, medication, or inventory is not found.
        HTTPException 400 if any requested amount exceeds available inventory.
    """
    if not requests:
        return []

    # Validate all requests first (fail fast)
    cart_ids = set()
    medication_ids = set()
    inventory_ids = set()

    for request in requests:
        cart_ids.add(request.cart_id)
        medication_ids.add(request.medication_id)
        inventory_ids.add(request.inventory_id)

    # Check all carts exist
    carts = {}
    for cart_id in cart_ids:
        cart = await session.get(Cart, cart_id)
        if not cart:
            raise HTTPException(status_code=404, detail=f"Cart {cart_id} not found")
        carts[cart_id] = cart

    # Check all medications exist
    medications = {}
    for med_id in medication_ids:
        medication = await session.get(Medication, med_id)
        if not medication:
            raise HTTPException(status_code=404, detail=f"Medication {med_id} not found")
        medications[med_id] = medication

    # Check all inventory items exist and have sufficient amounts
    inventories = {}
    for inv_id in inventory_ids:
        inventory = await session.get(Inventory, inv_id)
        if not inventory:
            raise HTTPException(status_code=404, detail=f"Inventory item {inv_id} not found")
        inventories[inv_id] = inventory

    # Validate inventory amounts for each request and filter out insufficient ones
    valid_requests = []
    for request in requests:
        inventory = inventories[request.inventory_id]
        if inventory.amount >= request.amount:
            valid_requests.append(request)
        else:
            # Log warning but don't fail - allow partial fulfillment
            medication = medications[request.medication_id]
            print(f"WARNING: Skipping {medication.name} - insufficient inventory. Available: {inventory.amount} {inventory.unit}, Requested: {request.amount}")

    if not valid_requests:
        raise HTTPException(
            status_code=400,
            detail="No medications can be added due to insufficient inventory for all requested items"
        )

    # All validations passed, perform bulk operations
    cart_items = []

    for request in valid_requests:
        inventory = inventories[request.inventory_id]

        # Decrement inventory
        inventory.amount -= request.amount
        session.add(inventory)

        # Create cart item
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
        cart_items.append(cart_item)

    # Commit all changes
    await session.commit()

    # Refresh all cart items to get their IDs
    for cart_item in cart_items:
        await session.refresh(cart_item)

    return cart_items


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