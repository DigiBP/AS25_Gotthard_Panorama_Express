from typing import List, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import HTTPException

from Application.backend.models.inventory import Inventory, InventoryCreate
from Application.backend.models.medication import Medication


async def get_all_inventory(session: AsyncSession) -> List[Inventory]:
    result = await session.exec(select(Inventory))
    return result.all()


async def get_inventory_by_id(session: AsyncSession, inventory_id: str) -> Optional[Inventory]:
    result = await session.exec(select(Inventory).where(Inventory.id == inventory_id))
    return result.one_or_none()


async def add_inventory(session: AsyncSession, inventory_data: InventoryCreate):
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


async def update_inventory_amount(session: AsyncSession, inventory_id: str, new_amount: float) -> Inventory:
    item = await get_inventory_by_id(session, inventory_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Inventory item '{inventory_id}' not found")

    item.amount = new_amount
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def delete_inventory(session: AsyncSession, inventory_id: str) -> None:
    item = await get_inventory_by_id(session, inventory_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Inventory item '{inventory_id}' not found")

    await session.delete(item)
    await session.commit()


async def delete_all_inventory(session: AsyncSession) -> int:
    result = await session.exec(select(Inventory))
    items = result.all()
    count = len(items)
    for item in items:
        await session.delete(item)
    await session.commit()
    return count