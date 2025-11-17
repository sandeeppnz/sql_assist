# repair_sql.py

from typing import Any
import json

from llm import get_llm
from schema_service import schema_service
from sql_utils import extract_sql 


def repair_sql(question: str, bad_sql: str, error_message: str) -> str:
    """
    Ask the LLM to repair an invalid SQL statement.

    - Keeps semantics aligned with the original question as much as possible.
    - Fixes unknown columns / wrong joins / misuse of DateKey/OrderDateKey.
    - Ensures the result is ONE safe SELECT (CTEs allowed).
    """
    llm = get_llm()

    system = (
        "You are a senior SQL Server T-SQL expert. "
        "Your job is to REPAIR a broken SELECT query so it compiles "
        "and matches the user's intent, using only the provided schema. "
        "You must not change the intent unless absolutely necessary to fix errors."
    )

    user = f"""
The user asked:

{question}

The previous SQL was:

{bad_sql}

The database or validator returned this error message:

{error_message}

Use ONLY the following schema info to choose tables, columns, and joins:

{schema_service.schema_text}

Key schema & modelling rules (very important):
- FactInternetSales / FactResellerSales use OrderDateKey (INT) which joins to DimDate.DateKey (INT).
- OrderDateKey / DateKey are surrogate keys, NOT datetime. 
  Never call YEAR(), DATEADD(), or other datetime functions directly on these keys.
  Instead:
  - JOIN DimDate AS d ON FactX.OrderDateKey = d.DateKey
  - Filter using d.CalendarYear or d.FullDateAlternateKey.
- Product categories:
  FactX.ProductKey → DimProduct.ProductKey →
  DimProductSubcategory.ProductSubcategoryKey →
  DimProductCategory.ProductCategoryKey.
- Customer geography:
  FactInternetSales.CustomerKey → DimCustomer.GeographyKey → DimGeography.
- Customer income / education:
  DimCustomer.YearlyIncome, DimCustomer.EnglishEducation live in DimCustomer.
- Do not invent columns. If an error says "Unknown columns: ...", replace them
  with the closest correct columns and/or joins implied by the schema.

Additional hints:
- If the error mentions "Unknown columns", fix the column names and/or joins.
- If the error mentions "Arithmetic overflow error converting expression to data type datetime",
  you are almost certainly treating an INT key as datetime. Replace logic like:
    YEAR(FactInternetSales.OrderDateKey) = 2004
  with a join to DimDate and filters on DimDate.CalendarYear or DimDate.FullDateAlternateKey.
- If the question asks for counts of orders, prefer COUNT(DISTINCT SalesOrderNumber)
  rather than COUNT(*) where appropriate.
- Preserve the grouping/aggregation intent of the original query whenever reasonable.

Your task:
- Produce a NEW SQL query that:
  - Is valid T-SQL for SQL Server.
  - Uses only existing tables/columns.
  - Keeps the semantics aligned with the question and the original SQL's intent.
- The final output MUST be a JSON object with two fields:
  - "sql": the repaired SQL string.
  - "explanation": a brief explanation of the fix.
- "sql" must contain ONE valid T-SQL SELECT (CTEs allowed, final statement SELECT).
- No prose outside of JSON. No backticks.
- Never use INSERT/UPDATE/DELETE/ALTER/DROP/TRUNCATE/EXEC/CREATE/MERGE.
"""

    raw = llm.generate(system, [{"role": "user", "content": user}])

    if not isinstance(raw, str):
        raw = str(raw)

    sql = extract_sql(raw)
    return sql.strip()
