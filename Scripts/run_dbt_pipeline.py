from prefect import flow
import os

@flow(name="DBT Transformation Runner")
def execute_dbt_pipeline():
    """
    Runs dbt transformation and tests using shell commands.
    """
    print("Running dbt transformations...")
    os.system("dbt run")
    print("Running dbt tests...")
    os.system("dbt test")

if __name__ == "__main__":
    execute_dbt_pipeline()
