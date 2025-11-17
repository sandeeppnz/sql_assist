# sql_generator.py

from __future__ import annotations

import json
import re
from typing import Any, Dict

from llm import get_llm
from schema_service import schema_service


def _strip_code_fences(text: str) -> str:
    """
    Remove leading/trailing ``` or ```json fences if present.
    """
    s = text.strip()
    if s.startswith("```"):
        # drop the first line (``` or ```json)
        parts = s.splitlines()
        if len(parts) >= 2:
            # remove first line
            s = "\n".join(parts[1:])
        # drop trailing ```
        if s.strip().endswith("```"):
            s = s.strip()
            s = s[: s.rfind("```")].strip()
    return s


def _extract_json_block(text: str) -> str | None:
    """
    Try to find a JSON object `{ ... }` inside `text` and return that substring.
    Handles cases where the model adds extra prose around the JSON.
    """
    s = text.strip()
    start = s.find("{")
    end = s.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return s[start : end + 1]


def _parse_sql_from_raw(raw: str) -> str:
    """
    Given the raw LLM output, try very hard to get the actual SQL string
    from a JSON object of the form {"sql": "...", "explanation": "..."}.
    If that fails, fall back to returning the raw string.
    """
    s = _strip_code_fences(raw)

    # 1) Try direct JSON parse
    try:
        obj = json.loads(s)
    except json.JSONDecodeError:
        # 2) Try to extract just the {...} part and parse that
        block = _extract_json_block(s)
        if block is None:
            return s.strip()
        try:
            obj = json.loads(block)
        except json.JSONDecodeError:
            return s.strip()

    # At this point we have some JSON object
    if not isinstance(obj, dict):
        return s.strip()

    sql_value: Any = obj.get("sql")
    if not isinstance(sql_value, str):
        return s.strip()

    sql_str = sql_value.strip()

    # Handle case where "sql" itself is a nested JSON string
    # e.g. "sql": "{\"sql\": \"SELECT ...\", \"explanation\": \"...\"}"
    if sql_str.startswith("{") and "\"sql\"" in sql_str:
        try:
            inner_obj: Dict[str, Any] = json.loads(sql_str)
            inner_sql = inner_obj.get("sql")
            if isinstance(inner_sql, str) and inner_sql.strip():
                return inner_sql.strip()
        except json.JSONDecodeError:
            pass

    return sql_str


def generate_sql(question: str) -> str:
    """
    Generate a single T-SQL SELECT statement from a natural language question.
    Ensures we only return the SQL string, even if the model wraps it in JSON.
    """
    llm = get_llm()

    system = "You are a cautious T-SQL assistant for Microsoft SQL Server."
    user = f"""User question:
{question}

Use ONLY the following schema info to choose tables, columns, and joins:

{schema_service.schema_text}

Rules:
- Output ONLY a JSON object with two fields: "sql" and "explanation".
- "sql" must contain ONE valid T-SQL SELECT (CTEs allowed, final statement SELECT).
- No prose outside JSON. No backticks.
- Use exact table and column names from the schema above.
- Do NOT invent tables or columns.
- Prefer DimCustomer.FirstName + DimCustomer.LastName for customer name, if relevant.
- Use DimDate.FullDateAlternateKey where date filtering is required.
- Add TOP 100 to avoid large scans when it makes sense.
- Never use INSERT/UPDATE/DELETE/ALTER/DROP/TRUNCATE/EXEC/CREATE/MERGE.
"""

    raw = llm.generate(system, [{"role": "user", "content": user}])

    if not isinstance(raw, str):
        raw = str(raw)

    sql = _parse_sql_from_raw(raw)
    return sql.strip()
