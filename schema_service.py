from sqlalchemy import inspect
from typing import Dict, List, Set
import glob
import os

from db import engine
from config import MAX_SCHEMA_TABLES, MAX_SCHEMA_COLS_PER_TABLE

class SchemaService:
    def __init__(self, engine):
        self.engine = engine
        self.tables: Set[str] = set()
        self.cols_by_table: Dict[str, List[str]] = {}
        self.fk_pairs: Set[tuple] = set()
        self.schema_text: str = ""
        self._load_schema()

    def _load_schema(self):
        """Introspect the live DB + read optional .sql files in ./data."""
        insp = inspect(self.engine)
        tables = insp.get_table_names()

        lines = []

        for t in tables[:MAX_SCHEMA_TABLES]:
            cols = [c["name"] for c in insp.get_columns(t)][:MAX_SCHEMA_COLS_PER_TABLE]
            self.cols_by_table[t] = cols
            self.tables.add(t)
            lines.append(f"- {t}: {', '.join(cols)}")

            for fk in insp.get_foreign_keys(t) or []:
                rt = fk.get("referred_table")
                lc = fk.get("constrained_columns") or []
                rc = fk.get("referred_columns") or []
                if rt and lc and rc:
                    for c1 in lc:
                        for c2 in rc:
                            self.fk_pairs.add((t, c1, rt, c2))
                            self.fk_pairs.add((rt, c2, t, c1))

        schema_text = "Known tables & columns (from live DB):\n" + "\n".join(lines)

        # Append any .sql DDL files from data/ as extra context (optional)
        ddl_chunks = []
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        for path in glob.glob(os.path.join(data_dir, "*.sql")):
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    ddl_chunks.append(f"-- From {os.path.basename(path)}\n" + f.read())
            except Exception:
                continue

        if ddl_chunks:
            schema_text += "\n\nAdditional DDL from data/*.sql:\n" + "\n\n".join(ddl_chunks)

        self.schema_text = schema_text

schema_service = SchemaService(engine)
