from fastapi import APIRouter
import httpx

router = APIRouter(prefix="", tags=["Utilities"])


@router.get("/health", summary="Health check endpoint")
async def health():
    """
    Health check endpoint to verify the API is running.

    Returns:
        dict: A status message indicating that the API is healthy.
    """
    return {"status": "ok"}


@router.post("/start_flow")
async def start_flow():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:5678/webhook-test/04ced486-2466-431f-b1fd-ea604848459b"
        )
        return {"status": response.status_code, "response": response.text}