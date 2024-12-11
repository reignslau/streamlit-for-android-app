import duckdb

def get_connection(token: str):
    """
    Establish and return a connection to the MotherDuck database.
    :param token: The MotherDuck token for authentication.
    :return: A DuckDB connection object.
    """
    try:
        connection = duckdb.connect(f"md:TestDB?motherduck_token={token}")
        return connection
    except Exception as e:
        raise RuntimeError(f"Failed to connect to MotherDuck: {e}")