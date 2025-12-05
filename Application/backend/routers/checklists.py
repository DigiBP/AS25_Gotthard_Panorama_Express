from fastapi import APIRouter, Depends, Body
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.core.database import get_session

router = APIRouter(prefix="/checklists", tags=["Checklists"])

