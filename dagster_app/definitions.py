from dagster import Definitions, ScheduleDefinition, define_asset_job, load_assets_from_modules

from dagster_app.assets import dbt, ingestion
from dagster_app.resources import dbt_resource, postgres_io_manager

dbt_assets = load_assets_from_modules([dbt])
ingestion_assets = load_assets_from_modules([ingestion])

# Define a job that materializes the ingestion assets
ingestion_job = define_asset_job(name="daily_ingestion_job", selection=ingestion_assets)

# Schedule the job to run daily at midnight
daily_schedule = ScheduleDefinition(
    job=ingestion_job,
    cron_schedule="0 0 * * *",  # Run at midnight every day
)

defs = Definitions(
    assets=[*dbt_assets, *ingestion_assets],
    resources={
        "io_manager": postgres_io_manager,
        "dbt": dbt_resource,
    },
)
