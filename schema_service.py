# schema_service.py

from sqlalchemy import inspect
from typing import Dict, List, Set

from db import engine
from config import MAX_SCHEMA_TABLES, MAX_SCHEMA_COLS_PER_TABLE


class SchemaService:
    def __init__(self, engine):
        self.engine = engine
        self.tables: Set[str] = set()
        self.cols_by_table: Dict[str, List[str]] = {}
        # fk_pairs holds tuples of (table1, column1, table2, column2)
        self.fk_pairs: Set[tuple] = set()
        self.schema_text: str = ""
        self._load_schema()

    def _load_schema(self) -> None:
        """
        Introspect the live DB and build a compact schema description
        for the LLM: tables, columns, and foreign-key relationships.

        This avoids dumping full DDL, which is noisy and can confuse
        the model, while staying perfectly consistent with what the
        validator uses.
        """
        insp = inspect(self.engine)
        tables = [
            t for t in insp.get_table_names()
            if t not in ("DatabaseLog", "sysdiagrams")
        ]

        lines: List[str] = []

        # 1) Table + column listing (bounded by MAX_* config values)
        for t in tables[:MAX_SCHEMA_TABLES]:
            cols = [c["name"] for c in insp.get_columns(t)][:MAX_SCHEMA_COLS_PER_TABLE]
            self.cols_by_table[t] = cols
            self.tables.add(t)
            lines.append(f"- {t}: {', '.join(cols)}")

            # 2) Collect foreign-key relationships
            for fk in insp.get_foreign_keys(t) or []:
                rt = fk.get("referred_table")
                lc = fk.get("constrained_columns") or []
                rc = fk.get("referred_columns") or []
                if rt and lc and rc:
                    for c1 in lc:
                        for c2 in rc:
                            # store both directions to help the LLM reason
                            self.fk_pairs.add((t, c1, rt, c2))
                            self.fk_pairs.add((rt, c2, t, c1))

        # 3) Human-readable schema text for the LLM
        schema_parts: List[str] = []

        schema_parts.append("Known tables & columns (from live DB):")
        schema_parts.append("\n".join(lines))

        # Add a FK section if we found any
        if self.fk_pairs:
            rel_lines: List[str] = []
            # sort for deterministic output
            for t1, c1, t2, c2 in sorted(self.fk_pairs):
                rel_lines.append(f"- {t1}.{c1} → {t2}.{c2}")

            schema_parts.append("\nKnown foreign-key relationships:")
            schema_parts.append("\n".join(rel_lines))

        # Join into a single text blob
        self.schema_text = "\n".join(schema_parts)


# Singleton instance used by the rest of the app
schema_service = SchemaService(engine)
