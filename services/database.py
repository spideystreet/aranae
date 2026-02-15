
import os
import psycopg2
from typing import List, Dict
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()

def get_db_connection():
    """Returns a connection to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DB")
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise

def fetch_latest_jobs(table_name: str = "raw_freework_jobs", limit: int = 5) -> List[Dict]:
    """Fetches the latest scraped jobs from the specified table."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = f"""
                SELECT job_id, title, company, publication_date, location, income, skills, contracts, start_date
                FROM {table_name}
                ORDER BY scraped_at DESC
                LIMIT %s
            """
            cur.execute(query, (limit,))
            return [dict(row) for row in cur.fetchall()]
    except Exception as e:
        print(f"Error fetching data from {table_name}: {e}")
        return []
    finally:
        conn.close()
