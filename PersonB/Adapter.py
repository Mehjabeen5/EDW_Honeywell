import pandas as pd
from pathlib import Path
from typing import Dict, List, Any

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

class MockCortexAdapter:
    """Simulates Snowflake Cortex Analyst using local CSVs."""
    def __init__(self, data_dir: Path = DATA_DIR):
        self.tables: Dict[str, pd.DataFrame] = {
            "revenue_qoq": pd.read_csv(data_dir / "revenue_qoq.csv"),
            "revenue_by_region": pd.read_csv(data_dir / "revenue_by_region.csv"),
            "revenue_by_product": pd.read_csv(data_dir / "revenue_by_product.csv"),
            "orders_qoq": pd.read_csv(data_dir / "orders_qoq.csv"),
        }

    def run_nl(self, nlq: str, dimension: str) -> List[Dict[str, Any]]:
        dim = (dimension or "").lower().strip()
        if dim == "time":
            return self.tables["revenue_qoq"].sort_values("period").tail(2).to_dict("records")
        if dim == "region":
            df = self.tables["revenue_by_region"]; latest = df["period"].max()
            return df[df["period"] == latest].sort_values("rev_delta_pct").to_dict("records")
        if dim == "product":
            df = self.tables["revenue_by_product"]; latest = df["period"].max()
            return df[df["period"] == latest].sort_values("rev_delta_pct").to_dict("records")
        if dim == "orders":
            return self.tables["orders_qoq"].sort_values("period").tail(2).to_dict("records")
        return []

