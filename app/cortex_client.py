from .session import get_session
from .config import CONFIG

def cortex_complete(prompt: str, model: str | None = None) -> str:
    """Thin wrapper around SNOWFLAKE.CORTEX.COMPLETE."""
    session = get_session()
    model_name = model or CONFIG.model_name

    # Escape single quotes so the prompt is safe in a SQL literal
    safe_prompt = prompt.replace("'", "''")

    query = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            '{model_name}',
            '{safe_prompt}'
        )
    """

    return session.sql(query).collect()[0][0]
