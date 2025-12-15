import json
import os
import logging
from typing import AsyncGenerator
from datetime import date

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.models.medication import Medication, MedicationCreate
from Application.backend.services.medication_service import create_medication
from Application.backend.models.inventory import Inventory, InventoryCreate
from Application.backend.services.inventory_service import add_inventory

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DATABASE_URL = "postgresql+asyncpg://gotthard_user:panorama_password@localhost:5432/express_database"

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True, future=True)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provides an async database session generator."""
    async with async_session_maker() as session:
        yield session

async def seed_medications(session: AsyncSession):
    """Seed medication data from JSON into the database, skipping existing entries."""
    json_path = os.path.join(os.path.dirname(__file__), "data", "medication_data_template.json")
    with open(json_path, "r", encoding="utf-8") as f:
        medication_data_list = json.load(f)

    inserted, skipped = 0, 0
    for item in medication_data_list:
        statement = select(Medication).where(Medication.medicationId == item["medicationId"])
        result = await session.exec(statement)
        if result.first():
            logger.warning(f"Skipping existing medication: {item['medicationId']}")
            skipped += 1
            continue

        await create_medication(session, MedicationCreate(**item))
        inserted += 1
        logger.info(f"Inserted medication: {item['medicationId']}")

    logger.info(f"Medication seed complete: {inserted} inserted, {skipped} skipped.")

async def seed_inventory(session: AsyncSession):
    """Seed inventory data from JSON into the database, skipping existing entries."""
    json_path = os.path.join(os.path.dirname(__file__), "data", "inventory.json")
    with open(json_path, "r", encoding="utf-8") as f:
        inventory_data_list = json.load(f)

    inserted, skipped = 0, 0
    for item in inventory_data_list:
        statement = select(Inventory).where(
            Inventory.batchNumber == item["batchNumber"],
            Inventory.medicationId == item["medicationId"]
        )
        result = await session.exec(statement)
        if result.first():
            logger.warning(f"Skipping existing inventory: batch={item['batchNumber']} medication={item['medicationId']}")
            skipped += 1
            continue

        await add_inventory(session, InventoryCreate(**item))
        inserted += 1
        logger.info(f"Inserted inventory: batch={item['batchNumber']} medication={item['medicationId']}")

    logger.info(f"Inventory seed complete: {inserted} inserted, {skipped} skipped.")

async def seed_carts(session: AsyncSession):
    """Seed carts from JSON, skipping existing entries for same patient and date."""
    from Application.backend.models.cart import CartCreate, Cart
    from Application.backend.services.cart_service import add_cart

    json_path = os.path.join(os.path.dirname(__file__), "data", "carts.json")
    with open(json_path, "r", encoding="utf-8") as f:
        cart_data_list = json.load(f)

    inserted, skipped = 0, 0
    for item in cart_data_list:
        operation_date = date.fromisoformat(item["operationDate"])
        statement = select(Cart).where(Cart.patientId == item["patientId"], Cart.operationDate == operation_date)
        if (await session.exec(statement)).first():
            logger.warning(f"Skipping existing cart: patient={item['patientId']} date={item['operationDate']}")
            skipped += 1
            continue

        cart_create = CartCreate(**{**item, "operationDate": operation_date})
        await add_cart(session, cart_create)
        inserted += 1
        logger.info(f"Inserted cart: patient={item['patientId']} date={item['operationDate']}")

    logger.info(f"Cart seed complete: {inserted} inserted, {skipped} skipped.")

async def seed_cart_items(session: AsyncSession):
    """Seed cart items from JSON, skipping existing entries."""
    from Application.backend.models.cart_item import AddToCartRequest, CartItem
    from Application.backend.services.cart_item_service import add_medication_to_cart

    json_path = os.path.join(os.path.dirname(__file__), "data", "cart_items.json")
    if not os.path.exists(json_path):
        logger.warning("cart_items.json not found — skipping cart_items seed.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        cart_item_data_list = json.load(f)

    inserted, skipped = 0, 0
    for item in cart_item_data_list:
        statement = select(CartItem).where(
            CartItem.cart_id == item["cart_id"],
            CartItem.inventory_id == item["inventory_id"],
            CartItem.medication_id == item["medication_id"]
        )
        if (await session.exec(statement)).first():
            logger.warning(f"Skipping existing cart_item: cart={item['cart_id']} inventory={item['inventory_id']} medication={item['medication_id']}")
            skipped += 1
            continue

        await add_medication_to_cart(session, AddToCartRequest(**item))
        inserted += 1
        logger.info(f"Inserted cart_item: cart={item['cart_id']} inventory={item['inventory_id']} medication={item['medication_id']}")

    logger.info(f"CartItem seed complete: {inserted} inserted, {skipped} skipped.")

async def init_db() -> None:
    """Create database tables and seed initial data."""
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: SQLModel.metadata.create_all(sync_conn, checkfirst=True))
    logger.info("Database tables created")

    async with async_session_maker() as session:
        await seed_medications(session)
        await seed_inventory(session)
        await seed_carts(session)
        await seed_cart_items(session)