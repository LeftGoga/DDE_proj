from sqlalchemy import select

def find_similar_records(session, model, query_embedding, top_n=5):
    """
    Find the most similar records to the query embedding in the given table model.

    Args:
        session: SQLAlchemy session object.
        model: SQLAlchemy ORM model representing the table.
        query_embedding: List of floats representing the query embedding.
        top_n: Number of similar records to return.

    Returns:
        List of similar records.
    """
    stmt = (
        select(model)
        .order_by(model.embedding.l2_distance(query_embedding))
        .limit(top_n)
    )
    results = session.scalars(stmt).all()
    return results