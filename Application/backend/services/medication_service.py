from typing import List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.models.medication import Medication, MedicationCreate


async def get_all_medications(session: AsyncSession) -> List[Medication]:
    """
    Retrieve all medications from the catalog.

    - **session**: Async database session.

    Returns a list of all `Medication` entries.
    """
    result = await session.exec(select(Medication))
    return result.all()


async def create_medication(session: AsyncSession, medication_data: MedicationCreate) -> Medication:
    """
    Create a new medication entry.

    - **session**: Async database session.
    - **medication_data**: Data required to create the medication.

    Returns the newly created `Medication` object.
    """
    medication = Medication(**medication_data.model_dump())
    session.add(medication)
    await session.commit()
    await session.refresh(medication)
    return medication