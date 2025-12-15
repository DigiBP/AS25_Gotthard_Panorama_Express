from pydantic import BaseModel

class ChecklistItem(BaseModel):
    checked: bool
    name: str
    location: str
    amount: float


class ChecklistItemResponse(BaseModel):
    checked: bool
    name: str
    location: str
    amount: float


CHECKLIST_EXAMPLE = [
    {
    "checked": False,
    "name": "Lidocaine",
    "location": "Unknown",
    "amount": 5
    },
    {
    "checked": False,
    "name": "Propofol",
    "location": "Unknown",
    "amount": 50
    },
    {
    "checked": False,
    "name": "Fentanyl",
    "location": "Unknown",
    "amount": 10
    }
]