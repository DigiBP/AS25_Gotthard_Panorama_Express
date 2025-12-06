from fastapi import APIRouter, Depends, Body
from typing import List
from Application.backend.core.database import get_session
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.models.checklist import ChecklistItem, ChecklistItemResponse, CHECKLIST_EXAMPLE
from Application.backend.services.checklist_service import process_checklist

router = APIRouter(prefix="/checklist", tags=["checklist"])


@router.post("/", response_model=List[ChecklistItemResponse])
async def evaluate_checklist(
    items: List[ChecklistItem] = Body(..., example=CHECKLIST_EXAMPLE),
    session: AsyncSession = Depends(get_session)
):
    return await process_checklist(items, session)

@router.post("/create" )
async def create_checklist_item():
    return  200