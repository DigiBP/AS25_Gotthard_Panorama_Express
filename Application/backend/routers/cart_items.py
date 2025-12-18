from typing import List

from fastapi import APIRouter, Body, Depends, Path
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.core.database import get_session
from Application.backend.models.cart_item import (
    CART_ITEM_EXAMPLE,
    AddToCartRequest,
    CartItem,
)
from Application.backend.services.cart_item_service import (
    add_medication_to_cart,
    add_medications_to_cart_bulk,
    get_all_cart_items,
    get_cart_contents,
    get_expiring_items,
    remove_cart_item,
)

router = APIRouter(prefix="/cart-items", tags=["Cart Items"])


@router.get("/", response_model=List[CartItem], summary="List all cart items")
async def list_cart_items(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all cart items in the system.

    - **session**: Async database session (automatically injected).

    Returns a list of `CartItem` objects.
    """
    return await get_all_cart_items(session)


@router.get("/expiring", response_model=List[CartItem], summary="List expiring cart items")
async def list_expiring_items(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all cart items that are expiring soon.

    - **session**: Async database session (automatically injected).

    Returns a list of `CartItem` objects with upcoming expiration.
    """
    return await get_expiring_items(session)


@router.get(
    "/cart/{cart_id}",
    response_model=List[CartItem],
    summary="Get contents of a specific cart",
)
async def list_cart_contents(
    cart_id: int = Path(..., description="ID of the cart to retrieve contents for"),
    session: AsyncSession = Depends(get_session),
):
    """
    Retrieve all items contained in a specific cart.

    - **cart_id**: ID of the cart.
    - **session**: Async database session (automatically injected).

    Returns a list of `CartItem` objects in the specified cart.
    """
    return await get_cart_contents(session, cart_id)


@router.post("/add", response_model=CartItem, summary="Add a medication to a cart")
async def add_to_cart(
    request: AddToCartRequest = Body(..., example=CART_ITEM_EXAMPLE, description="Data for the cart item to add"),
    session: AsyncSession = Depends(get_session),
):
    """
    Add a medication to a cart.

    - **request**: Cart item data (medication, amount, cart_id, etc.).
    - **session**: Async database session (automatically injected).

    Returns the newly added `CartItem`.
    """
    return await add_medication_to_cart(session, request)


@router.post("/add-bulk", response_model=List[CartItem], summary="Add multiple medications to a cart")
async def add_to_cart_bulk(
    requests: List[AddToCartRequest] = Body(..., description="List of cart item data to add"),
    session: AsyncSession = Depends(get_session),
):
    """
    Add multiple medications to a cart in a single request.

    - **requests**: List of cart item data (medication, amount, cart_id, etc.).
    - **session**: Async database session (automatically injected).

    Returns a list of the newly added `CartItem` objects.
    """
    return await add_medications_to_cart_bulk(session, requests)


@router.delete("/{cart_item_id}", summary="Remove a cart item")
async def remove_from_cart(
    cart_item_id: int = Path(..., description="ID of the cart item to remove"),
    session: AsyncSession = Depends(get_session),
):
    """
    Remove a specific item from the cart.

    - **cart_item_id**: ID of the cart item to remove.
    - **session**: Async database session (automatically injected).

    Returns a confirmation message upon successful removal.
    """
    await remove_cart_item(session, cart_item_id)
    return {"message": "Cart item removed successfully"}