from fastapi import APIRouter, Depends, Body, HTTPException
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.models.inventory import Inventory, InventoryCreate, INVENTORY_POST_EXAMPLE
from Application.backend.services.inventory_service import get_all_inventory, add_inventory, update_inventory_amount, delete_inventory, delete_all_inventory
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


@router.get("/", response_model=List[Inventory])
async def list_inventory(session: AsyncSession = Depends(get_session)):
    return await get_all_inventory(session)


@router.get("/{medication_id}", response_model=List[Inventory])
async def list_inventory_by_medication(medication_id: str, session: AsyncSession = Depends(get_session)):
    """Return inventory entries filtered by medication id."""
    return await get_inventory_by_medication(session, medication_id)

    

@router.post("/", response_model=Inventory)
async def add_inventory_item(
    inventory: InventoryCreate = Body(..., example=INVENTORY_POST_EXAMPLE),
    session: AsyncSession = Depends(get_session),
):
    return await add_inventory(session, inventory)


@router.patch("/{inventory_id}", response_model=Inventory)
async def update_inventory_item(
    inventory_id: int,
    new_amount: float = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
):
    updated_item = await update_inventory_amount(session, inventory_id, new_amount)
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return updated_item


@router.delete("/{inventory_id}", summary="Delete an inventory item")
async def delete_inventory_item(
    inventory_id: int,
    session: AsyncSession = Depends(get_session),
):
    await delete_inventory(session, inventory_id)
    return {"detail": f"Inventory item {inventory_id} deleted successfully"}


@router.delete("/", summary="Delete all inventory items")
async def delete_all_inventory_items(
    session: AsyncSession = Depends(get_session),
):
    count = await delete_all_inventory(session)
    return {"detail": f"{count} inventory items deleted successfully"}