# column_mappings.py

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ColumnMapping:
    """
    Describes how to rewrite a logical column reference like:

        <alias>.<column>

    into a physical expression and (optionally) add a JOIN.

    Fields:
        table:
            The *logical* table name used in the FROM/JOIN clause
            (e.g. "DimCustomer").

        column:
            The *logical* column name that may not physically exist
            on that table (e.g. "SalesRepCode").

        replacement:
            The SQL expression to use instead, with placeholders:
              - {alias}       → the original table alias (e.g. dc)
              - {extra_alias} → the alias we give to the joined table
            Example:
              "{extra_alias}.SalesRepresentativeCode"

        join_snippet:
            The JOIN clause to inject (if not already present), with
            the same placeholders:
              - {alias}
              - {extra_alias}
            Example:
              "LEFT JOIN DimSalesRep {extra_alias} "
              "ON {alias}.SalesRepKey = {extra_alias}.SalesRepKey"

            If join_snippet is None, only the column expression is
            rewritten and no JOIN is added.
    """
    table: str
    column: str
    replacement: str
    join_snippet: Optional[str] = None


# Global list of mappings used by sql_rewriter.apply_column_mappings()
COLUMN_MAPPINGS: List[ColumnMapping] = []


# --------------------------------------------------------------------
# Example: DimCustomer.SalesRepCode → DimSalesRepCode.SalesRepresentativeCode
# --------------------------------------------------------------------
#
# COLUMN_MAPPINGS.append(
#     ColumnMapping(
#         table="DimCustomer",           # table name as seen in FROM/JOIN
#         column="SalesRepCode",         # logical column LLM might use
#         replacement="{extra_alias}.SalesRepresentativeCode",
#         join_snippet=(
#             "LEFT JOIN DimSalesRepCode {extra_alias} "
#             "ON {alias}.SalesRepKey = {extra_alias}.SalesRepKey"
#         ),
#     )
# )
#
# After this:
#   Generated:
#       SELECT dc.SalesRepCode
#       FROM DimCustomer dc
#
#   Rewritten to something like:
#       SELECT src.SalesRepresentativeCode
#       FROM DimCustomer dc
#       LEFT JOIN DimSalesRepCode src
#         ON dc.SalesRepKey = src.SalesRepKey
#
# Adjust table names, key names, and column names above to match
# your actual schema before uncommenting / adding mappings.


# --------------------------------------------------------------------
# NEW: DimProduct.ProductName → DimProduct.<real name>
# --------------------------------------------------------------------
# If the LLM often generates dp.ProductName but your real column is,
# for example, DimProduct.ProductDescription, we can rewrite it:
#
#   dp.ProductName   →   dp.ProductDescription
#
# No extra JOIN is needed, so join_snippet=None.
# Change "ProductDescription" below to your actual column name if different.
COLUMN_MAPPINGS.append(
    ColumnMapping(
        table="DimProduct",              # as used in FROM/JOIN
        column="ProductName",            # logical name LLM may use
        replacement="{alias}.ProductDescription",  # REAL column name
        join_snippet=None
    )
)
