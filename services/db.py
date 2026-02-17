import os
import psycopg2
from dotenv import load_dotenv

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
