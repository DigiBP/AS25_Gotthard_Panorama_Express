from typing import List

from fastapi import APIRouter, Body, Depends, Path, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.core.database import get_session
from Application.backend.models.cart import CART_EXAMPLE, Cart, CartCreate, CartStatus
from Application.backend.services.cart_service import (
    add_cart,
    get_all_carts,
    update_cart_status,
    remove_cart,
)

router = APIRouter(prefix="/carts", tags=["Carts"])


@router.get("/", response_model=List[Cart], summary="List all carts")
async def list_carts(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all carts in the system.

    - **session**: Async database session (automatically injected).

    Returns a list of `Cart` objects.
    """
    return await get_all_carts(session)


@router.post("/", response_model=Cart, summary="Create a new cart")
async def create_cart(
    cart: CartCreate = Body(..., example=CART_EXAMPLE, description="Data for the cart to create"),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new cart.

    - **cart**: Cart creation data (e.g., name, type).
    - **session**: Async database session (automatically injected).

    Returns the newly created `Cart`.
    """
    return await add_cart(session, cart)


@router.patch("/{cart_id}/status", response_model=Cart, summary="Update cart status")
async def change_cart_status(
    cart_id: int = Path(..., description="ID of the cart to update"),
    new_status: CartStatus = Body(..., embed=True, description="New status for the cart"),
    session: AsyncSession = Depends(get_session),
):
    """
    Update the status of an existing cart.

    - **cart_id**: ID of the cart to update.
    - **new_status**: New status for the cart (`Prepared`, `In-Use`, or `Closed`).
    - **session**: Async database session (automatically injected).

    Returns the updated `Cart`.
    """
    return await update_cart_status(session, cart_id, new_status)


@router.delete("/{cart_id}", summary="Delete a cart")
async def delete_cart(
    cart_id: int = Path(..., description="ID of the cart to delete"),
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a cart by its ID.

    - **cart_id**: ID of the cart to remove.
    - **session**: Async database session (automatically injected).

    Returns a confirmation message upon successful deletion.
    """
    await remove_cart(session, cart_id)
    return {"message": "Cart deleted successfully"}


@router.put("/{cart_id}", response_model=Cart)
def update_cart(
    cart_id: int, cart_update: CartCreate, session: AsyncSession = Depends(get_session)
):
    cart = session.get(Cart, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    for key, value in cart_update.dict().items():
        setattr(cart, key, value)
    session.commit()
    session.refresh(cart)
    return cart
