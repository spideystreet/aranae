
import pandas as pd
from dagster import IOManager, InputContext, OutputContext
from sqlalchemy import create_engine

class PostgresPandasIOManager(IOManager):
    def __init__(self, user, password, host, port, db):
        self.connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db}"
        self.engine = create_engine(self.connection_string)

    def handle_output(self, context: OutputContext, obj: pd.DataFrame):
        table_name = context.asset_key.path[-1]
        schema = "public" # Default schema
        
        context.log.info(f"Writing dataframe to {schema}.{table_name}")
        # Append to table to build history. Deduplication will be handled in dbt.
        obj.to_sql(table_name, self.engine, schema=schema, if_exists="append", index=False)

    def load_input(self, context: InputContext) -> pd.DataFrame:
        table_name = context.asset_key.path[-1]
        schema = "public"
        return pd.read_sql(f"SELECT * FROM {schema}.{table_name}", self.engine)
