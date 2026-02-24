from dagster import AssetExecutionContext, AssetKey, MaterializeResult, asset

from scrapers.config import FREEWORK_FILTERED_URL
from scrapers.freework_scraper import fetch_jobs as fetch_freework_jobs
from scrapers.wttj_scraper import fetch_wttj_jobs
from services.ingestor import ingest_jobs


@asset(
    key=AssetKey(["free_work", "RAW_FREEWORK"]),
    group_name="ingestion",
    compute_kind="python",
)
def raw_freework_jobs(context: AssetExecutionContext) -> MaterializeResult:
    """Scrapes jobs from free-work.com (last 24h) and upserts into RAW_FREEWORK."""
    all_jobs = []
    for page in range(1, 4):
        jobs = fetch_freework_jobs(page=page, url=FREEWORK_FILTERED_URL)
        if not jobs:
            break
        all_jobs.extend(jobs)

    ingest_jobs(all_jobs, table_name="RAW_FREEWORK")
    context.log.info(f"Ingested {len(all_jobs)} freework jobs")
    return MaterializeResult(metadata={"num_jobs": len(all_jobs)})


@asset(
    key=AssetKey(["wttj", "RAW_WTTJ"]),
    group_name="ingestion",
    compute_kind="python",
)
def raw_wttj_jobs(context: AssetExecutionContext) -> MaterializeResult:
    """Scrapes jobs from Welcome to the Jungle (last 24h) and upserts into RAW_WTTJ."""
    jobs = fetch_wttj_jobs(pages=3)
    ingest_jobs(jobs, table_name="RAW_WTTJ")
    context.log.info(f"Ingested {len(jobs)} WTTJ jobs")
    return MaterializeResult(metadata={"num_jobs": len(jobs)})
