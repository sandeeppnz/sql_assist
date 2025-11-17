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
            The table name as it appears in the FROM/JOIN clause
            (e.g. "DimCustomer").

        column:
            The logical column name that may not physically exist
            on that table (e.g. "SalesRepCode").

        replacement:
            The SQL expression to use instead, with placeholders:
              - {alias}       → the original table alias (e.g. "dc")
              - {extra_alias} → the alias we give to a joined table
            Example:
              "{extra_alias}.SalesRepresentativeCode"

        join_snippet:
            Optional JOIN clause to inject if needed, with the same
            placeholders {alias} and {extra_alias}, e.g.:

              "LEFT JOIN DimSalesRepCode {extra_alias} "
              "ON {alias}.SalesRepKey = {extra_alias}.SalesRepKey"

            If join_snippet is None, only the column reference is
            rewritten and no JOIN is added.
    """
    table: str
    column: str
    replacement: str
    join_snippet: Optional[str] = None


# Global list of mappings used by sql_rewriter.apply_column_mappings()
COLUMN_MAPPINGS: List[ColumnMapping] = []


# --------------------------------------------------------------------
# Example (commented out): DimCustomer.SalesRepCode → DimSalesRepCode.SalesRepresentativeCode
# --------------------------------------------------------------------
#
# Uncomment and adapt if/when you actually have these tables/columns.
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


# --------------------------------------------------------------------
# DimProduct.ProductName → DimProduct.EnglishProductName
# --------------------------------------------------------------------
# The LLM often invents `dp.ProductName`, but in AdventureWorksDW, the
# actual column is `EnglishProductName`. No extra JOIN is needed.
COLUMN_MAPPINGS.append(
    ColumnMapping(
        table="DimProduct",                  # as used in FROM/JOIN
        column="ProductName",                # logical name LLM may use
        replacement="{alias}.EnglishProductName",
        join_snippet=None,
    )
)
