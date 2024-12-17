from configs import DB_PATH
DATABASE_URL = DB_PATH
import random
from loguru import logger
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from database.db_items import init_db_items,  ItemsEmbedding
from database.db_mechanics import init_db_rules, RulesEmbedding
from database.db_bestiary import init_db_creatures,  CreatureEmbedding
from database.db_spells import SpellEmbedding, init_db_spells
from database.query import find_similar_records
from database.update_db import update_database
from configs import CSV_PATHS


logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=''),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO",
)


engine = create_engine(DATABASE_URL)

def generate_query_embedding():

    logger.info("Generating a random query embedding.")
    embedding = [random.uniform(1.5, 1.9) for _ in range(312)]
    logger.success("Query embedding generated successfully.")
    return embedding

def initialize_databases():

    try:
        logger.info("Initializing bestiary database...")
        init_db_creatures(CSV_PATHS["bestiary"])
        logger.success("Bestiary database initialized successfully.")

        logger.info("Initializing spells database...")
        init_db_spells(CSV_PATHS["spells"])
        logger.success("Spells database initialized successfully.")

        logger.info("Initializing rules database...")
        init_db_rules(CSV_PATHS["rules"])
        logger.success("Rules database initialized successfully.")

        logger.info("Initializing items database...")
        init_db_items(CSV_PATHS["items"])
        logger.success("Items database initialized successfully.")

    except Exception as e:
        logger.error(f"An error occurred during database initialization: {e}")
        raise

def query_databases():

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        logger.info("Querying bestiary database...")
        query_embedding = generate_query_embedding()
        similar_creatures = find_similar_records(session, CreatureEmbedding, query_embedding, top_n=5)
        for creature in similar_creatures:
            logger.info(f"Bestiary: Name: {creature.name}, Description: {creature.description}")
        logger.success("Bestiary database queried successfully.")

        logger.info("Querying spells database...")
        query_embedding = generate_query_embedding()
        similar_spells = find_similar_records(session, SpellEmbedding, query_embedding, top_n=5)
        for spell in similar_spells:
            logger.info(f"Spells: Name: {spell.title}, Description: {spell.desc}")
        logger.success("Spells database queried successfully.")

        logger.info("Querying rules database...")
        query_embedding = generate_query_embedding()
        similar_rules = find_similar_records(session, RulesEmbedding, query_embedding, top_n=5)
        for rule in similar_rules:
            logger.info(f"Rules: Name: {rule.name}, Description: {rule.description}")
        logger.success("Rules database queried successfully.")

        logger.info("Querying items database...")
        query_embedding = generate_query_embedding()
        similar_items = find_similar_records(session, ItemsEmbedding, query_embedding, top_n=5)
        for item in similar_items:
            logger.info(f"Items: Name: {item.name}, Description: {item.description}")
        logger.success("Items database queried successfully.")

    except Exception as e:
        logger.error(f"An error occurred during database querying: {e}")
        raise
    finally:
        session.close()
        logger.info("Database session closed.")

def update_items():

    try:
        logger.info("Updating items database...")
        update_database(engine, ItemsEmbedding, CSV_PATHS["items"])
        logger.success("Items database updated successfully.")
    except Exception as e:
        logger.error(f"An error occurred while updating items database: {e}")
        raise

if __name__ == "__main__":
    try:
        logger.info("Starting database initialization.")
        initialize_databases()

        logger.info("Querying all databases.")
        query_databases()

        logger.info("Updating items database.")
        update_items()


        logger.info("Re-querying all databases after update.")
        query_databases()

        logger.success("All operations completed successfully.")
    except Exception as e:
        logger.critical(f"A critical error occurred: {e}")
