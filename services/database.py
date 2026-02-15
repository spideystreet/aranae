
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

def ingest_jobs(jobs: List[Dict], table_name: str = "raw_freework_jobs"):
    """Inserts a list of job dictionaries into the database."""
    if not jobs:
        print("No jobs to ingest.")
        return

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Prepare the insert query with ON CONFLICT to avoid duplicates
            insert_query = f"""
                INSERT INTO {table_name} (
                    job_id, title, company, publication_date, location, 
                    income, skills, contracts, start_date, url, source, description, scraped_at
                ) VALUES (
                    %(job_id)s, %(title)s, %(company)s, %(publication_date)s, %(location)s, 
                    %(income)s, %(skills)s, %(contracts)s, %(start_date)s, %(url)s, %(source)s, %(description)s, NOW()
                )
                ON CONFLICT (job_id) DO NOTHING;
            """
            
            # Convert list fields to comma-separated strings for storage
            processed_jobs = []
            for job in jobs:
                job_copy = job.copy()
                if isinstance(job_copy.get('contracts'), list):
                    job_copy['contracts'] = ', '.join(job_copy['contracts'])
                if isinstance(job_copy.get('skills'), list):
                    job_copy['skills'] = ', '.join(job_copy['skills'])
                processed_jobs.append(job_copy)

            cur.executemany(insert_query, processed_jobs)
            conn.commit()
            print(f"Successfully ingested {len(processed_jobs)} jobs into {table_name}.")
    except Exception as e:
        print(f"Error ingesting jobs into {table_name}: {e}")
        conn.rollback()
    finally:
        conn.close()
