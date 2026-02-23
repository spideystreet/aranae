
from scrapers.freework import fetch_jobs, CUSTOM_URL
import pandas as pd
from dagster import asset

@asset(group_name="ingestion", compute_kind="python")
def raw_freework_jobs() -> pd.DataFrame:
    """
    Scrapes jobs from free-work.com using the custom 24h filter filter.
    Returns a DataFrame.
    """
    all_jobs = []
    # Fetch first 3 pages (should cover 24h usually, or iterate until empty)
    # The user wants "every 24h", so we can assume we run this daily.
    # We fetch a few pages to be sure.
    for page in range(1, 4):
        jobs = fetch_jobs(page=page, url=CUSTOM_URL)
        if not jobs:
            break
        all_jobs.extend(jobs)
    
    df = pd.DataFrame(all_jobs)
    
    # Ensure columns exist even if empty
    expected_cols = ["job_id", "title", "company", "publication_date", "contracts", "skills", 
                     "duration", "experience_level", "income", "location", "description", "start_date", "url", "source"]
    
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None
    
    df['contracts'] = df['contracts'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
    df['skills'] = df['skills'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
    
    # Add ingestion timestamp
    df['scraped_at'] = pd.Timestamp.now()
    
    return df
