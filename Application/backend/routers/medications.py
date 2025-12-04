from fastapi import APIRouter, Depends, Body
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.core.database import get_session
from Application.backend.models.medication import Medication, MedicationCreate, MEDICATION_EXAMPLE
from Application.backend.services.medication_service import get_all_medications, create_medication

router = APIRouter(prefix="/medications", tags=["Medications"])


@router.get("/", response_model=List[Medication])
async def list_medications(session: AsyncSession = Depends(get_session)):
    return await get_all_medications(session)


@router.post(
    "/",
    response_model=Medication,
    summary="Create a new medication",
    description="Registers a new medication type in the catalog.",
)
async def add_medication(
    medication: MedicationCreate = Body(
        ...,
        example=MEDICATION_EXAMPLE,
    ),
    session: AsyncSession = Depends(get_session),
):
    return await create_medication(session, medication)