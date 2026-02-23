import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.schemas import JobSchema
from services.db import get_db_connection


def ingest_jobs(jobs: list[dict], table_name: str = "raw_jobs"):
    """
    Inserts a list of job dictionaries into the database using Pydantic validation.
    The table_name should typically be RAW_FREEWORK or RAW_WTTJ.
    """
    if not jobs:
        print("No jobs to ingest.")
        return

    # Validate and process jobs via Pydantic
    processed_jobs = []
    for job_data in jobs:
        try:
            job = JobSchema(**job_data)
            processed_jobs.append(job.to_db_dict())
        except Exception as e:
            print(f"Validation error for job {job_data.get('job_id')}: {e}")
            continue

    if not processed_jobs:
        print("No valid jobs to ingest.")
        return

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Prepare the insert query with ON CONFLICT to avoid duplicates
            # Using the unified table structure with (source, job_id) unique constraint
            insert_query = f"""
                INSERT INTO "{table_name}" (
                    job_id, title, company, publication_date, location, city, region,
                    income, skills, contracts, start_date, url, source, description, duration, experience_level, remote, scraped_at
                ) VALUES (
                    %(job_id)s, %(title)s, %(company)s, %(publication_date)s, %(location)s, %(city)s, %(region)s,
                    %(income)s, %(skills)s, %(contracts)s, %(start_date)s, %(url)s, %(source)s, %(description)s, %(duration)s, %(experience_level)s, %(remote)s, NOW()
                )
                ON CONFLICT (source, job_id) DO UPDATE SET 
                    scraped_at = NOW(),
                    title = EXCLUDED.title,
                    company = EXCLUDED.company,
                    publication_date = EXCLUDED.publication_date,
                    location = EXCLUDED.location,
                    city = EXCLUDED.city,
                    region = EXCLUDED.region,
                    income = EXCLUDED.income,
                    skills = EXCLUDED.skills,
                    contracts = EXCLUDED.contracts,
                    start_date = EXCLUDED.start_date,
                    url = EXCLUDED.url,
                    description = EXCLUDED.description,
                    duration = EXCLUDED.duration,
                    experience_level = EXCLUDED.experience_level,
                    remote = EXCLUDED.remote;
            """
            cur.executemany(insert_query, processed_jobs)

            conn.commit()
            print(f"Successfully ingested {len(processed_jobs)} jobs into {table_name}.")
    except Exception as e:
        print(f"Error ingesting jobs into {table_name}: {e}")
        conn.rollback()
    finally:
        conn.close()
