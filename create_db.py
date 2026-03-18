import os

import psycopg2


def ensure_database_exists():
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/employee_db")

    # Connect to default maintenance DB to create target DB if missing
    maintenance_url = database_url.rsplit("/", 1)[0] + "/postgres"
    target_db = database_url.rsplit("/", 1)[1]

    conn = psycopg2.connect(maintenance_url)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
            exists = cur.fetchone() is not None
            if exists:
                print("Database already exists:", target_db)
                return
            cur.execute(f'CREATE DATABASE "{target_db}"')
            print("Created database:", target_db)
    finally:
        conn.close()


if __name__ == "__main__":
    ensure_database_exists()

