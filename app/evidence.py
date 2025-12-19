import pandas as pd
from typing import Dict, Any

def build_evidence(rev: pd.DataFrame, reg: pd.DataFrame, prod: pd.DataFrame) -> Dict[str, Any]:
    """Convert analytics DataFrames into JSON-serializable evidence dict."""
    return {
        "by_quarter": rev.to_dict(orient="records"),
        "by_region": reg.to_dict(orient="records"),
        "by_product": prod.to_dict(orient="records"),
    }
