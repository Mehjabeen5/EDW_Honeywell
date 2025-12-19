import pandas as pd
from .session import get_session
from .config import CONFIG

def fetch_views():
    """Fetch analytics views from the configured database & schema."""
    session = get_session()
    db = CONFIG.db_name
    schema = CONFIG.schema_name

    rev = session.sql(f"""
        SELECT *
        FROM {db}.{schema}.V_REVENUE_BY_QUARTER
        ORDER BY QUARTER
    """).to_pandas()

    reg = session.sql(f"""
        SELECT *
        FROM {db}.{schema}.V_REVENUE_BY_REGION
        ORDER BY QUARTER, REGION
    """).to_pandas()

    prod = session.sql(f"""
        SELECT *
        FROM {db}.{schema}.V_REVENUE_BY_PRODUCT
        ORDER BY QUARTER, PRODUCT
    """).to_pandas()

    return rev, reg, prod
