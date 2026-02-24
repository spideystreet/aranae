from dagster import AssetSelection, DefaultScheduleStatus, Definitions, ScheduleDefinition, define_asset_job, load_assets_from_modules

from dagster_app.assets import dbt, ingestion
from dagster_app.resources import dbt_resource

dbt_assets = load_assets_from_modules([dbt])
ingestion_assets = load_assets_from_modules([ingestion])

# One job: ingestion → dbt transformations (Dagster respects the dependency graph)
daily_pipeline_job = define_asset_job(
    name="daily_pipeline_job",
    selection=AssetSelection.all(),
)

# 6h00 Paris (UTC+1 winter) = 05:00 UTC
daily_schedule = ScheduleDefinition(
    job=daily_pipeline_job,
    cron_schedule="0 5 * * *",
    default_status=DefaultScheduleStatus.RUNNING,
)

defs = Definitions(
    assets=[*dbt_assets, *ingestion_assets],
    resources={"dbt": dbt_resource},
    schedules=[daily_schedule],
)
