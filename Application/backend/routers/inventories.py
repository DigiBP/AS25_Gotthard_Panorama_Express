from fastapi import APIRouter, Depends, Body, HTTPException
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.models.inventory import Inventory, InventoryCreate, INVENTORY_POST_EXAMPLE
from Application.backend.services.inventory_service import (
    get_all_inventory,
    get_inventory_by_medication,
    add_inventory,
    update_inventory_amount,
    delete_inventory,
    delete_all_inventory,
)
from Application.backend.core.database import get_session

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/", response_model=List[Inventory], summary="List all inventory items")
async def list_inventory(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all inventory items in the system.

    Returns a list of `Inventory` objects containing medication ID, location, amount, and other details.
    """
    return await get_all_inventory(session)


@router.get("/{medication_id}", response_model=List[Inventory], summary="List inventory by medication ID")
async def list_inventory_by_medication(
    medication_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve all inventory entries filtered by a specific medication ID.

    - **medication_id**: ID of the medication to filter by.

    Returns a list of `Inventory` objects for the given medication.
    """
    return await get_inventory_by_medication(session, medication_id)


@router.post("/", response_model=Inventory, summary="Add a new inventory item")
async def add_inventory_item(
    inventory: InventoryCreate = Body(..., example=INVENTORY_POST_EXAMPLE),
    session: AsyncSession = Depends(get_session),
):
    """
    Add a new item to the inventory.

    - **inventory**: Inventory details including medication ID, location, and amount.

    Returns the newly created `Inventory` object.
    """
    return await add_inventory(session, inventory)


@router.patch("/{inventory_id}", response_model=Inventory, summary="Update inventory item amount")
async def update_inventory_item(
    inventory_id: int,
    new_amount: float = Body(..., embed=True, description="New amount for the inventory item"),
    session: AsyncSession = Depends(get_session),
):
    """
    Update the amount of a specific inventory item.

    - **inventory_id**: ID of the inventory item to update.
    - **new_amount**: New amount value.

    Returns the updated `Inventory` object. Raises 404 if item does not exist.
    """
    updated_item = await update_inventory_amount(session, inventory_id, new_amount)
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return updated_item


@router.delete("/{inventory_id}", summary="Delete a specific inventory item")
async def delete_inventory_item(
    inventory_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a specific inventory item by ID.

    - **inventory_id**: ID of the inventory item to delete.

    Returns a confirmation message.
    """
    await delete_inventory(session, inventory_id)
    return {"detail": f"Inventory item {inventory_id} deleted successfully"}


@router.delete("/", summary="Delete all inventory items")
async def delete_all_inventory_items(
    session: AsyncSession = Depends(get_session),
):
    """
    Delete all inventory items in the system.

    Returns the number of deleted items.
    """
    count = await delete_all_inventory(session)
    return {"detail": f"{count} inventory items deleted successfully"}