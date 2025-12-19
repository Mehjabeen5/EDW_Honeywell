from snowflake.snowpark.context import get_active_session

def get_session():
    """Return the active Snowpark session provided by Streamlit in Snowflake."""
    return get_active_session()
