from fastapi import APIRouter

router = APIRouter()

@router.get("/", summary="Root endpoint")
async def root():
    """
    Root endpoint of the API.

    Returns:
        dict: A welcome message from the API.
    """
    return {"message": "Hallo von FastAPI!"}


@router.get("/health", summary="Health check endpoint")
async def health():
    """
    Health check endpoint to verify the API is running.

    Returns:
        dict: A status message indicating that the API is healthy.
    """
    return {"status": "ok"}