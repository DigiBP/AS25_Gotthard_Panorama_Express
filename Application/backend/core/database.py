import json
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from Application.backend.models.medication import Medication, MedicationCreate
from Application.backend.services.medication_service import create_medication
from Application.backend.models.inventory import Inventory, InventoryCreate
from Application.backend.services.inventory_service import add_inventory

DATABASE_URL = "postgresql+asyncpg://gotthard_user:panorama_password@localhost:5432/express_database"

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True, future=True)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def seed_medications(session: AsyncSession):
    json_path = os.path.join(
        os.path.dirname(__file__),
        "data",
        "medication_data_template.json"
    )

    with open(json_path, "r", encoding="utf-8") as f:
        medication_data_list = json.load(f)

    inserted = 0
    skipped = 0

    for item in medication_data_list:
        medication_id = item["medicationId"]

        statement = select(Medication).where(Medication.medicationId == medication_id)
        result = await session.exec(statement)
        existing = result.first()

        if existing:
            print(f"Skipping existing medication: {medication_id}")
            skipped += 1
            continue

        med_create = MedicationCreate(**item)
        await create_medication(session, med_create)
        inserted += 1
        print(f"Inserted medication: {medication_id}")

    print(f"Medication seed complete: {inserted} inserted, {skipped} skipped.")


async def seed_inventory(session: AsyncSession):
    json_path = os.path.join(
        os.path.dirname(__file__),
        "data",
        "inventory.json"
    )

    with open(json_path, "r", encoding="utf-8") as f:
        inventory_data_list = json.load(f)

    inserted = 0
    skipped = 0

    for item in inventory_data_list:

        statement = select(Inventory).where(
            Inventory.batchNumber == item["batchNumber"],
            Inventory.medicationId == item["medicationId"]
        )
        result = await session.exec(statement)
        existing = result.first()

        if existing:
            print(f"Skipping existing inventory item: batch={item['batchNumber']} medication={item['medicationId']}")
            skipped += 1
            continue

        inv = InventoryCreate(**item)
        await add_inventory(session, inv)
        inserted += 1
        print(f"Inserted inventory: batch={item['batchNumber']} medication={item['medicationId']}")

    print(f"Inventory seed complete: {inserted} inserted, {skipped} skipped.")


async def seed_carts(session: AsyncSession):
    from Application.backend.models.cart import Cart, CartCreate
    from Application.backend.services.cart_service import add_cart
    from datetime import date

    json_path = os.path.join(
        os.path.dirname(__file__),
        "data",
        "carts.json"
    )

    with open(json_path, "r", encoding="utf-8") as f:
        cart_data_list = json.load(f)

    inserted = 0
    skipped = 0

    for item in cart_data_list:

        operation_date = date.fromisoformat(item["operationDate"])

        statement = select(Cart).where(
            Cart.patientId == item["patientId"],
            Cart.operationDate == operation_date
        )
        result = await session.exec(statement)
        existing = result.first()

        if existing:
            print(f"Skipping existing cart: patient={item['patientId']} date={item['operationDate']}")
            skipped += 1
            continue

        item_corrected = {
            **item,
            "operationDate": operation_date
        }

        cart_create = CartCreate(**item_corrected)
        await add_cart(session, cart_create)
        inserted += 1

        print(f"Inserted cart: patient={item['patientId']} date={item['operationDate']}")

    print(f"Cart seed complete: {inserted} inserted, {skipped} skipped.")


async def seed_cart_items(session: AsyncSession):
    from Application.backend.models.cart_item import AddToCartRequest, CartItem
    from Application.backend.services.cart_item_service import add_medication_to_cart

    json_path = os.path.join(
        os.path.dirname(__file__),
        "data",
        "cart_items.json"
    )

    if not os.path.exists(json_path):
        print("cart_items.json not found — skipping cart_items seed.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        cart_item_data_list = json.load(f)

    inserted = 0
    skipped = 0

    for item in cart_item_data_list:

        statement = select(CartItem).where(
            CartItem.cart_id == item["cart_id"],
            CartItem.inventory_id == item["inventory_id"],
            CartItem.medication_id == item["medication_id"]
        )
        result = await session.exec(statement)
        existing = result.first()

        if existing:
            print(
                f"Skipping existing cart_item: cart={item['cart_id']} "
                f"inventory={item['inventory_id']} medication={item['medication_id']}"
            )
            skipped += 1
            continue

        req = AddToCartRequest(**item)

        await add_medication_to_cart(session, req)
        inserted += 1

        print(
            f"Inserted cart_item: cart={item['cart_id']} "
            f"inventory={item['inventory_id']} medication={item['medication_id']}"
        )

    print(f"CartItem seed complete: {inserted} inserted, {skipped} skipped.")


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: SQLModel.metadata.create_all(sync_conn, checkfirst=True))
    print("Database tables created")

    async with async_session_maker() as session:
        await seed_medications(session)
        await seed_inventory(session)
        await seed_carts(session)
        await seed_cart_items(session)