# sql_validator.py

import re
from typing import Tuple, List, Dict

from db import run_query
from schema_service import schema_service


# ---------------------------------------------------------
# 1. SQL Safety (no destructive ops)
# ---------------------------------------------------------

SQL_UPPER = (
    " INSERT ", " UPDATE ", " DELETE ", " ALTER ", " DROP ", " TRUNCATE ",
    " CREATE ", " MERGE ", " EXEC ", " EXECUTE ", " GRANT ", " REVOKE ",
    " BACKUP ", " RESTORE "
)

SQL_START_RE = re.compile(r"(?is)^\s*(with|select)\b")


def is_safe_select(sql: str) -> bool:
    """
    Ensure the generated SQL is a SELECT/CTE and does not contain
    obviously destructive operations.
    """
    lowered = sql.strip().lower()
    if not SQL_START_RE.search(lowered):
        return False

    padded = " " + lowered + " "
    return not any(op.lower() in padded for op in SQL_UPPER)


# ---------------------------------------------------------
# 2. Table Extraction & Validation
# ---------------------------------------------------------

TABLE_NAME_RE = re.compile(
    r'\bfrom\s+([\w\.\[\]]+)|\bjoin\s+([\w\.\[\]]+)',
    re.I
)


def extract_tables(sql: str) -> set:
    """
    Extract table identifiers (without schema) from FROM/JOIN clauses.
    Example: [dbo].[DimCustomer] -> DimCustomer
    """
    raw = set()
    for m in TABLE_NAME_RE.finditer(sql):
        g = m.group(1) or m.group(2)
        if g:
            ident = g.split('.')[-1].strip('[]')
            raw.add(ident)
    return raw


def has_unknown_tables(sql: str) -> Tuple[bool, List[str]]:
    """
    True + list if any tables in the SQL are not known to schema_service.
    """
    used = extract_tables(sql)
    unknown = [t for t in used if t not in schema_service.tables]
    return bool(unknown), unknown


# ---------------------------------------------------------
# 3. Alias Extraction (used for column validation & rewriter)
# ---------------------------------------------------------

# FROM <table> <alias>
# JOIN <table> <alias>
TABLE_ALIAS_RE = re.compile(
    r'\b(from|join)\s+([\w\.\[\]]+)(?:\s+(?:as\s+)?([\w\[\]]+))?',
    re.I
)


def _extract_alias_to_table(sql: str) -> Dict[str, str]:
    """
    Map SQL aliases -> actual table names.

    Handles patterns like:
      FROM FactInvoice fi
      JOIN [dbo].[DimCustomer] AS dc
      FROM DimCustomer           (no alias -> alias == table name)
    """
    mapping: Dict[str, str] = {}

    for m in TABLE_ALIAS_RE.finditer(sql):
        table_token = m.group(2)
        alias_token = m.group(3)

        if not table_token:
            continue

        table_name = table_token.split('.')[-1].strip('[]')
        alias = alias_token.strip('[]') if alias_token else table_name

        mapping[alias] = table_name

    return mapping


# ---------------------------------------------------------
# 4. Column-level Validation
# ---------------------------------------------------------

# alias.column or table.column
COLUMN_REF_RE = re.compile(
    r'([A-Za-z0-9_\[\]]+)\.([A-Za-z0-9_\[\]]+)',
    re.IGNORECASE,
)


def has_unknown_columns(sql: str) -> Tuple[bool, List[Tuple[str, str, str]]]:
    """
    Detects alias.column references that do not exist in schema_service.

    Returns:
        (has_unknown, [(table_name, alias_used, column_name), ...])

    Example element:
        ("DimCustomer", "dc", "SalesRepCode")
    """
    alias_to_table = _extract_alias_to_table(sql)
    unknown: List[Tuple[str, str, str]] = []

    if not alias_to_table:
        return False, unknown

    for m in COLUMN_REF_RE.finditer(sql):
        alias = m.group(1).strip('[]')
        col = m.group(2).strip('[]')

        # Determine the table behind this alias/prefix
        if alias in alias_to_table:
            table_name = alias_to_table[alias]
        elif alias in schema_service.tables:
            table_name = alias
        else:
            # Could be db/schema prefix; ignore
            continue

        # If table unknown, let table-level validation handle it
        if table_name not in schema_service.tables:
            continue

        valid_cols = schema_service.cols_by_table.get(table_name, [])

        if col not in valid_cols:
            unknown.append((table_name, alias, col))

    return bool(unknown), unknown


# ---------------------------------------------------------
# 5. SQL Server Preflight (compile-only)
# ---------------------------------------------------------

def _escape_for_tsql_literal(sql: str) -> str:
    return sql.replace("'", "''")


def server_preflight_ok(sql: str) -> Tuple[bool, str]:
    """
    Uses sp_describe_first_result_set to ask SQL Server to compile the
    query without executing it. Catches syntax / compile-time errors.
    """
    try:
        tsql = (
            "DECLARE @q nvarchar(max) = N'"
            + _escape_for_tsql_literal(sql)
            + "'; EXEC sp_describe_first_result_set @tsql = @q;"
        )
        _ = run_query(tsql)
        return True, "ok"
    except Exception as ex:
        return False, str(ex)


# ---------------------------------------------------------
# Exported symbols
# ---------------------------------------------------------

__all__ = [
    "is_safe_select",
    "extract_tables",
    "has_unknown_tables",
    "has_unknown_columns",
    "server_preflight_ok",
    "_extract_alias_to_table",
]
