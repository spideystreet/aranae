from pathlib import Path

from dagster_dbt import DbtProject

DBT_PROJECT_DIR = Path(__file__).parent.parent.joinpath("dbt")
DBT_PROJECT = DbtProject(
    project_dir=DBT_PROJECT_DIR,
)
