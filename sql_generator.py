from llm import get_llm
from schema_service import schema_service

def generate_sql(question: str) -> str:
    """Generate a single T-SQL SELECT statement from a natural language question."""
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
- Prefer DimCustomer.AccountName for customer name, if relevant.
- Use DimDate.FullDateAlternateKey where date filtering is required.
- Add TOP 100 to avoid large scans when it makes sense.
- Never use INSERT/UPDATE/DELETE/ALTER/DROP/TRUNCATE/EXEC/CREATE/MERGE.
"""

    raw = llm.generate(system, [{"role": "user", "content": user}]).strip()

    # Try to parse JSON; fall back to raw content if necessary
    import json
    try:
        obj = json.loads(raw)
        sql = str(obj.get("sql", "")).strip()
        if sql:
            return sql
    except json.JSONDecodeError:
        pass

    # Fallback: assume the model returned plain SQL
    return raw.strip()
