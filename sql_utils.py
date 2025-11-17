# sql_utils.py
from __future__ import annotations

from typing import Any
import json


def _strip_markdown_fences(text: str) -> str:
    """
    Remove ``` or ```sql fences from around the SQL, if present.
    Handles both:
      ```sql
      SELECT ...
      ```
    and
      ```
      SELECT ...
      ```
    """
    text = text.strip()

    if not text.startswith("```"):
        return text

    lines = text.splitlines()

    # Drop first line (``` or ```sql)
    if lines:
        lines = lines[1:]

    # If the next line is just 'sql' / 'tsql', drop that too
    if lines and lines[0].strip().lower() in ("sql", "tsql"):
        lines = lines[1:]

    # Drop trailing ``` lines
    while lines and lines[-1].strip().startswith("```"):
        lines.pop()

    return "\n".join(lines).strip()


def _strip_explanation_tail(text: str) -> str:
    """
    Handle the very common shape we see in your results:

      SELECT ... ORDER BY ... DESC",
        "explanation": "This query ...

    or any line starting with `"explanation":`.
    We drop the explanation line and any trailing JSON/comma rubbish.
    """
    lower = text.lower()
    exp_pos = lower.find('"explanation"')
    if exp_pos == -1:
        return text

    # Cut at the newline before the "explanation" key (if any)
    nl_before = text.rfind("\n", 0, exp_pos)
    if nl_before != -1:
        text = text[:nl_before]
    else:
        text = text[:exp_pos]

    text = text.rstrip()

    # Strip trailing comma or quote fragments from the previous line
    while text and text[-1] in ',;"':
        text = text[:-1].rstrip()

    return text


def _try_extract_inner_json(text: str, depth: int) -> str | None:
    """
    In some cases the model returns a JSON blob as a string, e.g.:

      "{ \"sql\": \"SELECT ...\", \"explanation\": \"...\" }"

    This tries to find such a JSON object inside the string and extract its `sql`.
    """
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace == -1 or last_brace == -1 or last_brace <= first_brace:
        return None

    json_str = text[first_brace:last_brace + 1]
    try:
        obj = json.loads(json_str)
    except Exception:
        return None

    inner = obj.get("sql") or obj.get("SQL")
    if not inner:
        return None

    return extract_sql(inner, depth + 1)


def extract_sql(raw: Any, depth: int = 0) -> str:
    """
    Robustly extract a single T-SQL statement (SELECT / WITH ... SELECT)
    from an LLM response.

    Handles:
      - dicts: {"sql": "...", "explanation": "..."}
      - nested JSON-in-string
      - markdown fences ``` ... ```
      - explanation tails appended to the SQL string
      - miscellaneous trailing junk after the main query

    This is *idempotent* – calling it multiple times is safe.
    """
    if depth > 8:
        # Safety guard against weird recursive structures
        return str(raw).strip()

    # 1) If it's already a dict, unwrap "sql"/"SQL" and recurse
    if isinstance(raw, dict):
        inner = raw.get("sql") or raw.get("SQL")
        if inner is None:
            return ""
        return extract_sql(inner, depth + 1)

    # 2) Treat as text from here
    text = str(raw).strip()
    if not text:
        return text

    # 3) Strip markdown fences if present
    text = _strip_markdown_fences(text)

    # 4) Try to parse an embedded JSON object and extract its "sql"
    inner = _try_extract_inner_json(text, depth)
    if inner is not None:
        return inner.strip()

    # 5) Strip any explanation tail (",\n  "explanation": "...")
    text = _strip_explanation_tail(text)

    # 6) Now locate the start of the SQL: first WITH or SELECT
    lowered = text.lower()
    sel_idx = lowered.find("select")
    with_idx = lowered.find("with")

    candidates = [i for i in (with_idx, sel_idx) if i != -1]
    start_idx = min(candidates) if candidates else -1

    if start_idx == -1:
        # No obvious SELECT/WITH; just return whatever is left
        return text.strip()

    sql_part = text[start_idx:]

    # 7) If there is a semicolon, trim anything after the last ';'
    semi_idx = sql_part.rfind(";")
    if semi_idx != -1:
        sql_part = sql_part[:semi_idx + 1]

    # 8) Final cleanup: strip stray backticks/quotes at edges
    sql_part = sql_part.strip()
    while sql_part and sql_part[-1] in "`'\"":
        # Don't touch normal single quotes used for strings in the middle –
        # this is only trimming trailing fence/quote noise.
        if sql_part.endswith("''"):  # avoid breaking valid '' literals
            break
        sql_part = sql_part[:-1].rstrip()

    return sql_part
