from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import pandas as pd
from config import DATABASE_URL

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Please configure it in your environment.")


engine: Engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def run_query(sql: str) -> pd.DataFrame:
    """Run a SQL query and return a pandas DataFrame."""
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)
    return df
