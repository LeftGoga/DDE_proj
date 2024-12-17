import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import ast

def validate_embedding_for_update(embedding_str, expected_dim=312):
    """Validate and clean the embedding for database updates."""
    try:
        embedding = ast.literal_eval(embedding_str)  # Parse the string into a Python list
        if not isinstance(embedding, list):
            raise ValueError("Embedding is not a list")
        embedding = [float(x) for x in embedding]  # Ensure all elements are floats
        if len(embedding) > expected_dim:
            return embedding[:expected_dim]  # Truncate
        elif len(embedding) < expected_dim:
            return embedding + [0.0] * (expected_dim - len(embedding))  # Pad
        return embedding
    except Exception as e:
        print(f"Invalid embedding during update: {embedding_str}. Error: {e}")
        return [0.0] * expected_dim  # Default to zero-vector if invalid


def update_database(engine, model, csv_path):
    """
    Update the database with new data from a CSV file.

    Args:
        engine: SQLAlchemy engine object.
        model: SQLAlchemy ORM model representing the table.
        csv_path: Path to the CSV file containing new data.
    """
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Load and validate the CSV
        df = pd.read_csv(csv_path,keep_default_na=False)

        df['embeddings'] = df['embeddings'].apply(validate_embedding_for_update)

        # Check required columns
        required_columns = [column.name for column in model.__table__.columns if column.name != 'id']
        for column in required_columns:
            if column not in df.columns:
                raise ValueError(f"CSV must have a '{column}' column.")

        # Check for existing records or add new ones
        has_id_column = 'id' in df.columns

        for _, row in df.iterrows():
            try:
                if has_id_column and pd.notna(row['id']):
                    # Find the existing record by ID
                    existing_record = session.query(model).filter_by(id=row['id']).first()

                    if existing_record:
                        # Update the record fields
                        for column in required_columns:
                            setattr(existing_record, column, row.get(column, ''))
                    else:
                        # Insert a new record
                        new_record = model(**{column: row.get(column, '') for column in required_columns})
                        session.add(new_record)
                else:
                    # Insert a new record if 'id' is not provided
                    new_record = model(**{column: row.get(column, '') for column in required_columns})
                    session.add(new_record)

            except Exception as e:
                print(f"Error updating/inserting row: {row}. Error: {e}")

        session.commit()
        print(f"Database updated successfully from {csv_path}.")

    except Exception as e:
        print(f"An error occurred during the update: {e}")

    finally:
        session.close()
