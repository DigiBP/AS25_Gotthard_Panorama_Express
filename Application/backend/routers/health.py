from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Health check endpoint")
async def health():
    """
    Health check endpoint to verify the API is running.

    Returns:
        dict: A status message indicating that the API is healthy.
    """
    return {"status": "ok"}
