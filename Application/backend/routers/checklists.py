from fastapi import APIRouter, Depends, Body, HTTPException
from typing import List, Dict, Any
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


@router.put("/")
async def update_checklist_file(items: List[Dict[str, Any]] = Body(...)):
    """
    Update the checklist.json file with the provided JSON data.
    
    Expects a list of dicts, e.g., [{"checked": false, "name": "Lidocaine", "location": "Cabinet A1", "amount": 5}, ...]
    """
    import json
    import os
    
    file_path = os.path.join(os.path.dirname(__file__), "../../frontend/src/views/checklist.json")
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        return {"status": "Checklist file updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update file: {str(e)}")


@router.get("/", response_model=List[Dict[str, Any]])
async def get_checklist():
    """
    Retrieve the current checklist data from checklist.json.
    """
    import json
    import os
    
    file_path = os.path.join(os.path.dirname(__file__), "../../frontend/src/views/checklist.json")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Checklist file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")
