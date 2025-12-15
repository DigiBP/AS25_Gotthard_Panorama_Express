from typing import List, Optional
from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.models.inventory import Inventory, InventoryCreate
from Application.backend.models.medication import Medication


async def get_all_inventory(session: AsyncSession) -> List[Inventory]:
    """
    Retrieve all inventory items.

    - **session**: Async database session.

    Returns a list of all `Inventory` entries.
    """
    result = await session.exec(select(Inventory))
    return result.all()


async def get_inventory_by_id(session: AsyncSession, inventory_id: str) -> Optional[Inventory]:
    """
    Retrieve a single inventory item by its ID.

    - **session**: Async database session.
    - **inventory_id**: ID of the inventory item.

    Returns the `Inventory` item or `None` if not found.
    """
    result = await session.exec(select(Inventory).where(Inventory.id == inventory_id))
    return result.one_or_none()


async def add_inventory(session: AsyncSession, inventory_data: InventoryCreate) -> Inventory:
    """
    Add a new inventory item.

    Ensures that the referenced medication exists before creating
    the inventory entry.

    - **session**: Async database session.
    - **inventory_data**: Inventory data to create.

    Raises:
        HTTPException 404 if the medication does not exist.

    Returns the created `Inventory` item.
    """
    result = await session.exec(
        select(Medication).where(Medication.medicationId == inventory_data.medicationId)
    )
    medication = result.one_or_none()

    if not medication:
        raise HTTPException(
            status_code=404,
            detail=f"Medication '{inventory_data.medicationId}' not found"
        )

    item = Inventory(**inventory_data.model_dump())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def get_inventory_by_medication(session: AsyncSession, medication_id: str) -> List[Inventory]:
    """
    Retrieve all inventory items for a specific medication.

    - **session**: Async database session.
    - **medication_id**: Medication identifier.

    Returns a list of matching `Inventory` entries.
    """
    result = await session.exec(select(Inventory).where(Inventory.medicationId == medication_id))
    return result.all()


async def update_inventory_amount(session: AsyncSession, inventory_id: str, new_amount: float) -> Inventory:
    """
    Update the available amount of an inventory item.

    - **session**: Async database session.
    - **inventory_id**: ID of the inventory item.
    - **new_amount**: New amount to set.

    Raises:
        HTTPException 404 if the inventory item does not exist.

    Returns the updated `Inventory` item.
    """
    item = await get_inventory_by_id(session, inventory_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Inventory item '{inventory_id}' not found")

    item.amount = new_amount
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def delete_inventory(session: AsyncSession, inventory_id: str) -> None:
    """
    Delete a single inventory item.

    - **session**: Async database session.
    - **inventory_id**: ID of the inventory item.

    Raises:
        HTTPException 404 if the inventory item does not exist.
    """
    item = await get_inventory_by_id(session, inventory_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Inventory item '{inventory_id}' not found")

    await session.delete(item)
    await session.commit()


async def delete_all_inventory(session: AsyncSession) -> int:
    """
    Delete all inventory items.

    - **session**: Async database session.

    Returns the number of deleted inventory items.
    """
    result = await session.exec(select(Inventory))
    items = result.all()
    count = len(items)

    for item in items:
        await session.delete(item)

    await session.commit()
    return count