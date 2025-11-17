# sql_generator.py

from typing import Any, Dict
import json

from llm import get_llm
from schema_service import schema_service
from sql_utils import extract_sql  


def generate_sql(question: str) -> str:
    """
    Generate a single T-SQL SELECT statement from a natural language question.
    Ensures we only return the SQL string, even if the model wraps it in JSON.
    """
    llm = get_llm()

    system = (
        "You are a cautious T-SQL assistant for Microsoft SQL Server. "
        "You must generate one safe SELECT query (CTEs allowed) using *only* "
        "the provided schema. Use DimDate for any date filtering instead of "
        "treating surrogate keys (OrderDateKey, DateKey) as datetime."
    )

    # Anchored examples to steer table selection AND join patterns.
    examples = r"""
Example 1
Question: Total Internet Sales Amount for calendar year 2004
Answer:
{
  "sql": "SELECT SUM(fis.SalesAmount) AS TotalInternetSalesAmount
          FROM FactInternetSales AS fis
          JOIN DimDate AS d ON fis.OrderDateKey = d.DateKey
          WHERE d.CalendarYear = 2004;",
  "explanation": "Use FactInternetSales joined to DimDate and filter by CalendarYear."
}

Example 2
Question: Total Reseller Sales Amount in 2004
Answer:
{
  "sql": "SELECT SUM(frs.SalesAmount) AS TotalResellerSalesAmount
          FROM FactResellerSales AS frs
          JOIN DimDate AS d ON frs.OrderDateKey = d.DateKey
          WHERE d.CalendarYear = 2004;",
  "explanation": "Use FactResellerSales joined to DimDate and filter by CalendarYear."
}

Example 3
Question: Internet Sales Amount by Product Category in 2004
Answer:
{
  "sql": "SELECT pc.EnglishProductCategoryName,
                 SUM(fis.SalesAmount) AS TotalSalesAmount
          FROM FactInternetSales AS fis
          JOIN DimDate AS d ON fis.OrderDateKey = d.DateKey
          JOIN DimProduct AS p ON fis.ProductKey = p.ProductKey
          JOIN DimProductSubcategory AS psc
               ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
          JOIN DimProductCategory AS pc
               ON psc.ProductCategoryKey = pc.ProductCategoryKey
          WHERE d.CalendarYear = 2004
          GROUP BY pc.EnglishProductCategoryName
          ORDER BY TotalSalesAmount DESC;",
  "explanation": "Product categories come from DimProductCategory via DimProductSubcategory."
}

Example 4
Question: Internet Sales Amount by customer education level in 2004
Answer:
{
  "sql": "SELECT c.EnglishEducation,
                 SUM(fis.SalesAmount) AS TotalSalesAmount
          FROM FactInternetSales AS fis
          JOIN DimCustomer AS c ON fis.CustomerKey = c.CustomerKey
          JOIN DimDate AS d ON fis.OrderDateKey = d.DateKey
          WHERE d.CalendarYear = 2004
          GROUP BY c.EnglishEducation
          ORDER BY TotalSalesAmount DESC;",
  "explanation": "Education attributes live in DimCustomer, not DimDate."
}

Example 5
Question: Top 10 cities by Internet Sales Amount in 2004
Answer:
{
  "sql": "SELECT TOP 10 g.City,
                 g.StateProvinceName,
                 g.EnglishCountryRegionName,
                 SUM(fis.SalesAmount) AS TotalSalesAmount
          FROM FactInternetSales AS fis
          JOIN DimCustomer AS c ON fis.CustomerKey = c.CustomerKey
          JOIN DimGeography AS g ON c.GeographyKey = g.GeographyKey
          JOIN DimDate AS d ON fis.OrderDateKey = d.DateKey
          WHERE d.CalendarYear = 2004
          GROUP BY g.City, g.StateProvinceName, g.EnglishCountryRegionName
          ORDER BY TotalSalesAmount DESC;",
  "explanation": "City and geography come from DimGeography, joined via DimCustomer."
}

Example 6
Question: Total number of Internet Sales orders in 2004
Answer:
{
  "sql": "SELECT COUNT(DISTINCT fis.SalesOrderNumber) AS OrderCount
          FROM FactInternetSales AS fis
          JOIN DimDate AS d ON fis.OrderDateKey = d.DateKey
          WHERE d.CalendarYear = 2004;",
  "explanation": "When counting orders, use COUNT(DISTINCT SalesOrderNumber)."
}
"""

    user = f"""{examples}

Now answer this new question in the same JSON format.

User question:
{question}

Use ONLY the following schema info to choose tables, columns, and joins:

{schema_service.schema_text}

Mapping hints (very important):
- "Internet Sales" / "online sales" → use FactInternetSales (SalesAmount).
- "Reseller Sales" / "reseller orders" → use FactResellerSales (SalesAmount).
- "Sales quota" / "quota" → use FactSalesQuota (SalesAmountQuota).
- "Survey" / "survey responses" → use FactSurveyResponse.
- "Inventory" / "stock" / "balance" → use FactProductInventory (UnitsBalance).
- Product categories: FactInternetSales/FactResellerSales → DimProduct → DimProductSubcategory → DimProductCategory.
- Customer geography (city, country, state) → DimCustomer → DimGeography.
- Customer income / education → DimCustomer.
- Dates: FactX.OrderDateKey/DateKey → DimDate.DateKey → filter using DimDate.CalendarYear or DimDate.FullDateAlternateKey.

Do NOT use FactSurveyResponse unless the question is explicitly about survey data.

Rules:
- Output ONLY a JSON object with two fields: "sql" and "explanation".
- "sql" must contain ONE valid T-SQL SELECT (CTEs allowed, final statement SELECT).
- No prose outside JSON. No backticks.
- Use exact table and column names from the schema above.
- Do NOT invent tables or columns.
- NEVER treat OrderDateKey or DateKey as datetime (e.g. no YEAR(fis.OrderDateKey)).
  Always join to DimDate and filter on DimDate.CalendarYear or DimDate.FullDateAlternateKey.
- When the question asks for "orders", prefer COUNT(DISTINCT SalesOrderNumber) rather than COUNT(*).
- Prefer DimCustomer.FirstName + DimCustomer.LastName for customer names when relevant.
- Add TOP 100 to avoid large scans when it makes sense (for ranking-style questions).
- Never use INSERT/UPDATE/DELETE/ALTER/DROP/TRUNCATE/EXEC/CREATE/MERGE.
"""

    raw = llm.generate(system, [{"role": "user", "content": user}])

    sql = extract_sql(raw)
    return sql.strip()


