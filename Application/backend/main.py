from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Application.backend.routers import health, medications, inventories, orders, carts, cart_items, checklists
from Application.backend.core.database import init_db


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


app.include_router(health.router)
app.include_router(medications.router)
app.include_router(inventories.router)
app.include_router(orders.router)
app.include_router(carts.router)
app.include_router(cart_items.router)
app.include_router(checklists.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)