from dotenv import load_dotenv
load_dotenv("../.env")
import time
from loguru import logger
from prefect import flow, task

from parsing.main import parse_all
from preprocessing.preprocessing import preprocess_all
from database.load_db import initialize_databases


logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=''),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO",
)

@task
def parse_site_to_jsons():
    """
    Task to parse a site and generate JSON files.
    """
    start_time = time.time()
    try:
        logger.info("Starting task: Parsing site into JSON files.")
        parse_all()
        elapsed_time = time.time() - start_time
        logger.success(f"Task completed: Parsing site into JSON files in {elapsed_time:.2f} seconds.")
    except Exception as e:
        logger.error(f"Error during parsing site into JSON files: {e}")
        raise

@task
def preprocess_jsons_to_csv():
    """
    Task to preprocess JSON files into CSV format.
    """
    start_time = time.time()
    try:
        logger.info("Starting task: Preprocessing JSON files into CSV format.")
        preprocess_all()
        elapsed_time = time.time() - start_time
        logger.success(f"Task completed: Preprocessing JSON files into CSV format in {elapsed_time:.2f} seconds.")
    except Exception as e:
        logger.error(f"Error during preprocessing JSON files: {e}")
        raise

@task
def create_tables_and_load_csv():
    """
    Task to create database tables and load CSV files into them.
    """
    start_time = time.time()
    try:
        logger.info("Starting task: Creating database tables and loading CSV files.")
        initialize_databases()
        elapsed_time = time.time() - start_time
        logger.success(f"Task completed: Creating database tables and loading CSV files in {elapsed_time:.2f} seconds.")
    except Exception as e:
        logger.error(f"Error during creating database tables or loading CSV files: {e}")
        raise

@flow
def data_processing_workflow():
    """
    Orchestrates the full data processing workflow.
    """
    workflow_start_time = time.time()
    logger.info("Workflow started: Data processing workflow initiated.")

    try:
        # Step 1: Parse site into JSONs
        logger.info("Step 1: Parsing site into JSON files.")
        parse_site_to_jsons()

        # Step 2: Preprocess JSONs into CSVs
        logger.info("Step 2: Preprocessing JSON files into CSV files.")
        preprocess_jsons_to_csv()

        # Step 3: Create tables and load CSVs
        logger.info("Step 3: Creating database tables and loading CSV files.")
        create_tables_and_load_csv()

        workflow_elapsed_time = time.time() - workflow_start_time
        logger.success(f"Workflow completed successfully in {workflow_elapsed_time:.2f} seconds.")
    except Exception as e:
        logger.critical(f"Workflow failed due to an error: {e}")
        raise

if __name__ == "__main__":
    # Execute the workflow

    data_processing_workflow()
