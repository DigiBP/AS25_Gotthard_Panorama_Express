from typing import List

from fastapi import APIRouter, Body, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.core.database import get_session
from Application.backend.models.medication import MEDICATION_EXAMPLE, Medication, MedicationCreate
from Application.backend.services.medication_service import create_medication, get_all_medications

router = APIRouter(prefix="/medications", tags=["Medications"])


@router.get("/", response_model=List[Medication], summary="List all medications")
async def list_medications(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all registered medications from the catalog.

    - **session**: Async database session (automatically injected).

    Returns a list of `Medication` objects.
    """
    return await get_all_medications(session)


@router.post("/", response_model=Medication, summary="Create a new medication")
async def add_medication(
    medication: MedicationCreate = Body(
        ...,
        example=MEDICATION_EXAMPLE,
        description="Medication data to create a new entry in the catalog",
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Register a new medication in the catalog.

    - **medication**: Medication data to register.
    - **session**: Async database session (automatically injected).

    Returns the created `Medication` object.
    """
    return await create_medication(session, medication)