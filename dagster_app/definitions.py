from dagster import Definitions, ScheduleDefinition, define_asset_job, load_assets_from_modules

from dagster_app.assets import dbt, ingestion
from dagster_app.resources import dbt_resource

dbt_assets = load_assets_from_modules([dbt])
ingestion_assets = load_assets_from_modules([ingestion])

ingestion_job = define_asset_job(name="daily_ingestion_job", selection=ingestion_assets)

daily_schedule = ScheduleDefinition(
    job=ingestion_job,
    cron_schedule="0 0 * * *",
)

defs = Definitions(
    assets=[*dbt_assets, *ingestion_assets],
    resources={"dbt": dbt_resource},
    schedules=[daily_schedule],
)
