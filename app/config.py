from dataclasses import dataclass

@dataclass
class AppConfig:
    model_name: str = "snowflake-arctic"
    db_name: str = "EDW_2_DB"
    schema_name: str = "REASONING"

CONFIG = AppConfig()
