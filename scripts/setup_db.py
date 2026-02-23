import sys
from pathlib import Path

# Allow importing from services module
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.db import get_db_connection


def create_tables():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            tables = ["RAW_FREEWORK", "RAW_WTTJ"]
            for table in tables:
                print(f"Creating table {table} if not exists...")
                create_query = f"""
                CREATE TABLE IF NOT EXISTS "{table}" (
                    id SERIAL PRIMARY KEY,
                    job_id VARCHAR(255) NOT NULL,
                    source VARCHAR(50) NOT NULL,
                    title TEXT,
                    company TEXT,
                    publication_date TEXT,
                    location TEXT,
                    city TEXT,
                    region TEXT,
                    income TEXT,
                    skills TEXT,
                    contracts TEXT,
                    start_date TEXT,
                    url TEXT,
                    description TEXT,
                    duration TEXT,
                    experience_level TEXT,
                    remote TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT "unique_{table}_job" UNIQUE (source, job_id)
                );
                """
                cur.execute(create_query)
                print(f"Table {table} created/verified.")

        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    create_tables()
