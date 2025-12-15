from fastapi import HTTPException
from typing import List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func
from pathlib import Path
import aiofiles
import json

from Application.backend.models.inventory import Inventory
from Application.backend.models.medication import Medication
from Application.backend.models.checklist import ChecklistItem, ChecklistItemResponse

BASE_PATH = Path("core/data/medication_lists")
BASE_PATH.mkdir(parents=True, exist_ok=True)


async def process_checklist(items: List[ChecklistItem], session: AsyncSession) -> List[ChecklistItemResponse]:
    """
    Evaluate a checklist against the current medication inventory.

    - **items**: List of `ChecklistItem` objects to evaluate.
    - **session**: Async database session.

    Returns a list of `ChecklistItemResponse` objects indicating whether each item
    is available in inventory and the location of the medication.
    """
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


async def create_medication_checklist(
    checklist_name: str,
    items: List[ChecklistItem],
) -> List[ChecklistItemResponse]:
    """
    Create and save a new medication checklist to the filesystem.

    - **checklist_name**: Name of the checklist to create.
    - **items**: List of `ChecklistItem` objects to save.

    Raises:
        HTTPException 409 if a checklist with the same name already exists.

    Returns:
        List of `ChecklistItemResponse` objects representing the saved checklist.
    """
    filename = checklist_name.lower()
    file_path = BASE_PATH / f"{filename}.json"

    if file_path.exists():
        raise HTTPException(status_code=409, detail="Checklist already exists")

    response_items = [
        ChecklistItemResponse(
            checked=item.checked,
            name=item.name,
            location=item.location,
            amount=item.amount
        )
        for item in items
    ]

    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        await f.write(
            json.dumps(
                [item.model_dump() for item in response_items],
                indent=2,
                ensure_ascii=False
            )
        )

    return response_items


async def list_medication_checklists() -> List[str]:
    """
    Return the list of existing checklist names (without .json extension).

    Returns:
        List of checklist names as strings.
    """
    return sorted(file.stem for file in BASE_PATH.glob("*.json") if file.is_file())


async def get_medication_checklist(name: str) -> list[ChecklistItemResponse]:
    """
    Retrieve the content of a specific medication checklist.

    - **name**: Name of the checklist to retrieve.

    Raises:
        HTTPException 404 if the checklist does not exist.

    Returns:
        List of `ChecklistItemResponse` objects representing the checklist.
    """
    filename = name.strip().lower().replace(" ", "-")
    file_path = BASE_PATH / f"{filename}.json"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Checklist not found")

    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
        data = await f.read()
        items = json.loads(data)
        return [ChecklistItemResponse(**item) for item in items]