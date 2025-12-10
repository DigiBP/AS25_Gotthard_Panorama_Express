import os

import pandas as pd
from sqlalchemy import create_engine, text


def get_engine(db_params):
    """Creates and returns the SQLAlchemy engine."""
    conn_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"
    return create_engine(conn_string)


def truncate_table(engine, table_name):
    """
    Deletes all rows from a table without deleting the table structure.
    Also resets the index/id if RESTART IDENTITY is used (optional).
    """
    try:
        with engine.connect() as conn:
            print(f"⚠️ Deleteing content table '{table_name}'...")

            sql_query = text(f"DELETE FROM {table_name};")

            conn.execute(sql_query)
            conn.commit()  # Essential to finalize the deletion
            print(f"Table '{table_name}' emptied successfully.")

    except Exception as e:
        print(f"Error truncating table: {e}")


def push_db_to_postgres(df, table_name, engine, truncate_first=False):
    """
    Pushes df to a PostgreSQL database.
    """
    if truncate_first:
        truncate_table(engine, table_name)

    # if_exists options: 'fail', 'replace', 'append'
    df.to_sql(name=table_name, con=engine, if_exists="append", index=False)

    print(f"Success! Data uploaded to {table_name}.")


# Database Credentials

DB_CONFIG = {
    "dbname": "express_database",
    "user": "gotthard_user",
    "password": "panorama_password",
    "host": "localhost",
    "port": "5432",
}


order_to_delete = ["inventory", "medications", "carts", "cart_items"]
DESTINATION_TABLES = ["medications", "inventory", "carts", "cart_items"]
engine = get_engine(DB_CONFIG)

for table in order_to_delete:
    truncate_table(engine, table)


for table in DESTINATION_TABLES:
    df = pd.read_json(
        f"./Application/backend/init_jsons/{table}.json",
    )

    push_db_to_postgres(df, table, engine, truncate_first=False)
