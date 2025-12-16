from contextlib import asynccontextmanager
import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Application.backend.core.database import init_db
from Application.backend.routers import (
    cart_items,
    carts,
    checklists,
    utils,
    inventories,
    medications,
    notifications,
    orders,
    frontend,
)

from Application.backend.worker import start_camunda_workers

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    start_camunda_workers()
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

# Include all sub-routers into the Master router
api_router.include_router(medications.router)
api_router.include_router(inventories.router)
api_router.include_router(orders.router)
api_router.include_router(carts.router)
api_router.include_router(cart_items.router)
api_router.include_router(checklists.router)
api_router.include_router(notifications.router)

app.include_router(api_router)
app.include_router(frontend.router)
app.include_router(utils.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)