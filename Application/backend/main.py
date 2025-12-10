import os
from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from Application.backend.core.database import init_db
from Application.backend.routers import (
    cart_items,
    carts,
    checklists,
    health,
    inventories,
    medications,
    orders,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


origins = [
    "http://localhost:5173",  # Standard Vite/Vue port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")

# 2. Include all your sub-routers into the Master router
# Note: If your sub-routers already have prefixes (like prefix="/carts"),
# they will automatically combine to become "/api/carts"
api_router.include_router(health.router)
api_router.include_router(medications.router)
api_router.include_router(inventories.router)
api_router.include_router(orders.router)
api_router.include_router(carts.router)
api_router.include_router(cart_items.router)
api_router.include_router(checklists.router)

# 3. Include the Master router into the App
app.include_router(api_router)


@app.post("/start_flow")
async def start_flow():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:5678/webhook-test/04ced486-2466-431f-b1fd-ea604848459b"
        )
        return {"status": response.status_code, "response": response.text}


# VUEJS frontend
dist_directory = os.path.join(os.path.dirname(__file__), "./public")

if os.path.exists(os.path.join(dist_directory, "assets")):
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(dist_directory, "assets")),
        name="assets",
    )


@app.get("/front")
async def serve_spa_root():
    # If user types /front, we serve the index
    return FileResponse(os.path.join(dist_directory, "index.html"))


@app.get("/front/{full_path:path}")
async def serve_spa_subpath(full_path: str):
    # This catches /front/login, /front/user/123, etc.

    # Optional: Check if a physical file exists (like favicon inside dist root)
    file_path = os.path.join(dist_directory, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)

    return FileResponse(os.path.join(dist_directory, "index.html"))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
