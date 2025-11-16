# sql_rewriter.py

import re
from typing import Tuple

from column_mappings import COLUMN_MAPPINGS, ColumnMapping
from sql_validator import _extract_alias_to_table


# Used to find where to inject JOINs (before WHERE/GROUP BY/ORDER BY/HAVING)
JOIN_INSERT_RE = re.compile(r"\b(where|group by|order by|having)\b", re.IGNORECASE)


def apply_column_mappings(sql: str) -> Tuple[str, bool]:
    """
    Apply logical->physical column mappings defined in COLUMN_MAPPINGS.

    For each mapping, we look for occurrences of:

        <alias>.<column>

    where <alias> refers to the mapping.table in the FROM/JOIN clause.

    If found:
      - Replace it with mapping.replacement, substituting:
          {alias}       -> actual alias in the query, e.g. "dc"
          {extra_alias} -> synthetic alias we'll create for the joined table
      - If join_snippet is provided, ensure that JOIN is present in the SQL
        (inject it if not).

    Returns:
        (new_sql, changed)
    """
    alias_to_table = _extract_alias_to_table(sql)
    if not alias_to_table or not COLUMN_MAPPINGS:
        return sql, False

    new_sql = sql
    changed_any = False

    for mapping in COLUMN_MAPPINGS:
        # For each alias that refers to mapping.table, try to rewrite
        for alias, table_name in alias_to_table.items():
            if table_name != mapping.table:
                continue

            # Pattern for alias.column (e.g., dc.SalesRepCode)
            pattern = rf"\b{re.escape(alias)}\.{re.escape(mapping.column)}\b"

            # Quick check: if not present, no need to do work
            if not re.search(pattern, new_sql):
                continue

            # Use a stable extra alias for this mapping & alias combination
            # e.g., "dc" -> "dc_x"
            extra_alias = f"{alias}_x"

            # 1) Replace column reference
            replacement_expr = mapping.replacement.format(
                alias=alias,
                extra_alias=extra_alias,
            )

            new_sql, n_subs = re.subn(pattern, replacement_expr, new_sql)
            if n_subs > 0:
                changed_any = True

                # 2) Inject JOIN if needed
                if mapping.join_snippet:
                    join_clause = mapping.join_snippet.format(
                        alias=alias,
                        extra_alias=extra_alias,
                    )
                    # Avoid injecting the same JOIN twice
                    if join_clause not in new_sql:
                        new_sql = _inject_join(new_sql, join_clause)

    return new_sql, changed_any


def _inject_join(sql: str, join_clause: str) -> str:
    """
    Inject a JOIN clause into the SQL.

    Strategy:
      - Insert the join_clause before the first WHERE/GROUP BY/ORDER BY/HAVING
        if any of those exist.
      - Otherwise, append at the end of the FROM/JOIN block (i.e., end of SQL).

    join_clause should be a complete fragment like:

        "LEFT JOIN DimSalesRepCode src ON dc.SalesRepKey = src.SalesRepKey"
    """
    match = JOIN_INSERT_RE.search(sql)
    if match:
        idx = match.start()
        return sql[:idx].rstrip() + "\n" + join_clause + "\n" + sql[idx:]
    else:
        # No WHERE/GROUP BY/etc: append to the end
        return sql.rstrip() + "\n" + join_clause + "\n"
