from typing import List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func

from Application.backend.models.inventory import Inventory
from Application.backend.models.medication import Medication
from Application.backend.models.checklist import ChecklistItem, ChecklistItemResponse


async def process_checklist(items: List[ChecklistItem], session: AsyncSession) -> List[ChecklistItemResponse]:
    response_list: List[ChecklistItemResponse] = []

    for item in items:
        name = item.name
        required_amount = item.amount

        medication_query = select(Medication).where(func.lower(Medication.name) == name.lower())
        result = await session.exec(medication_query)
        medication = result.first()

        if not medication:
            response_list.append(
                ChecklistItemResponse(
                    checked=False,
                    name=name,
                    medication_id="None",
                    location="Unknown",
                    amount=required_amount
                )
            )
            continue

        inventory_query = select(Inventory).where(Inventory.medicationId == medication.medicationId)
        inventory_result = await session.exec(inventory_query)
        inventory_item = inventory_result.first()

        if not inventory_item:
            response_list.append(
                ChecklistItemResponse(
                    checked=False,
                    name=name,
                    medication_id=medication.medicationId,
                    location="Unknown",
                    amount=required_amount
                )
            )
            continue

        available = inventory_item.amount

        if available >= required_amount:
            response_list.append(
                ChecklistItemResponse(
                    checked=True,
                    name=name,
                    medication_id=medication.medicationId,
                    location=inventory_item.location,
                    amount=required_amount
                )
            )
        else:
            deficit = available - required_amount

            response_list.append(
                ChecklistItemResponse(
                    checked=False,
                    name=name,
                    medication_id=medication.medicationId,
                    location=inventory_item.location,
                    amount=deficit
                )
            )

    return response_list