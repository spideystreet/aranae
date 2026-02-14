
import os
from dagster_dbt import DbtCliResource
from dagster_app.constants import DBT_PROJECT
from dagster_app.io_managers import PostgresPandasIOManager

postgres_io_manager = PostgresPandasIOManager(
    user=os.getenv("POSTGRES_USER", "postgres"),
    password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=os.getenv("POSTGRES_PORT", "5432"),
    db=os.getenv("POSTGRES_DB", "postgres")
)

dbt_resource = DbtCliResource(project_dir=DBT_PROJECT)
