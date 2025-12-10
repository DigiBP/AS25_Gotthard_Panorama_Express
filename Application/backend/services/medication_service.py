from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from typing import List

from Application.backend.models.medication import Medication, MedicationCreate


async def get_all_medications(session: AsyncSession) -> List[Medication]:
    statement = select(Medication)
    results = await session.exec(statement)
    return results.scalars().all()


async def create_medication(
    session: AsyncSession,
    medication_data: MedicationCreate
) -> Medication:

    medication = Medication(**medication_data.dict())
    session.add(medication)
    await session.commit()
    await session.refresh(medication)
    return medication