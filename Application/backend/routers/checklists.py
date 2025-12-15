from fastapi import APIRouter, Depends, Body, Path
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.core.database import get_session
from Application.backend.models.checklist import ChecklistItem, ChecklistItemResponse, CHECKLIST_EXAMPLE
from Application.backend.services.checklist_service import (
    process_checklist,
    create_medication_checklist,
    list_medication_checklists,
    get_medication_checklist
)

router = APIRouter(prefix="/checklist", tags=["Checklist"])


@router.post("/", response_model=List[ChecklistItemResponse], summary="Evaluate a checklist")
async def evaluate_checklist(
    items: List[ChecklistItem] = Body(..., example=CHECKLIST_EXAMPLE, description="List of checklist items to evaluate"),
    session: AsyncSession = Depends(get_session),
):
    """
    Evaluate a checklist against the current medication inventory.

    Checks each item in the checklist and returns whether the required amount
    of each medication is available.

    - **items**: List of checklist items.
    - **session**: Async database session.

    Returns a list of `ChecklistItemResponse` objects indicating availability.
    """
    return await process_checklist(items, session)


@router.post("/{name}", response_model=List[ChecklistItemResponse], summary="Create a new checklist")
async def create_checklist(
    name: str = Path(..., description="Name of the checklist (used as filename, converted to lowercase)"),
    items: List[ChecklistItem] = Body(..., example=CHECKLIST_EXAMPLE, description="List of checklist items to save"),
):
    """
    Create and save a new medication checklist.

    - **name**: Checklist name.
    - **items**: Items to store in the checklist.

    Returns the saved checklist as a list of `ChecklistItemResponse`.
    Raises HTTP 409 if a checklist with the same name already exists.
    """
    return await create_medication_checklist(name, items)


@router.get("/all", response_model=List[str], summary="List all checklists")
async def get_checklists():
    """
    Retrieve all existing medication checklists.

    Returns a list of checklist names (without the .json extension).
    """
    return await list_medication_checklists()


@router.get("/{name}", response_model=List[ChecklistItemResponse], summary="Get a specific checklist")
async def get_checklist(
    name: str = Path(..., description="Name of the checklist to retrieve")
):
    """
    Retrieve the content of a specific medication checklist.

    - **name**: Name of the checklist.

    Returns a list of `ChecklistItemResponse`.
    Raises HTTP 404 if the checklist does not exist.
    """
    return await get_medication_checklist(name)


@router.get("/", response_model=List[ChecklistItemResponse], summary="Get the default checklist")
async def get_default_checklist():
    """
    Retrieve the default medication checklist.

    Returns the checklist named "default" as a list of `ChecklistItemResponse`.
    Raises HTTP 404 if it does not exist.
    """
    return await get_medication_checklist("default")