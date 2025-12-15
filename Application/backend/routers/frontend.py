from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os


router = APIRouter(prefix="/front", tags=["Frontend"])


# VUEJS frontend
dist_directory = os.path.join(os.path.dirname(__file__), "../public")

if os.path.exists(os.path.join(dist_directory, "assets")):
    router.mount(
        "/assets",
        StaticFiles(directory=os.path.join(dist_directory, "assets")),
        name="assets",
    )


@router.get("/")
async def serve_spa_root():
    return FileResponse(os.path.join(dist_directory, "index.html"))


@router.get("/{full_path:path}")
async def serve_spa_subpath(full_path: str):
    # This catches /front/login, /front/user/123, etc.
    file_path = os.path.join(dist_directory, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)

    return FileResponse(os.path.join(dist_directory, "index.html"))