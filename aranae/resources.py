from dagster_dbt import DbtCliResource

from aranae.constants import DBT_PROJECT

dbt_resource = DbtCliResource(project_dir=DBT_PROJECT)
