from llm import get_llm
from schema_service import schema_service

def repair_sql(question: str, bad_sql: str, error_msg: str) -> str:
    """Ask the LLM to repair an invalid SQL query using the DB error and schema."""
    llm = get_llm()

    system = "You are a SQL repair assistant for Microsoft SQL Server."
    user = f"""The following SQL is invalid for our schema or failed to compile:

--- QUESTION ---
{question}

--- BAD SQL ---
{bad_sql}

--- ERROR ---
{error_msg}

Here is the ONLY schema you may use:

{schema_service.schema_text}

Task:
- Generate a NEW T-SQL query that fixes the error.
- Output ONLY the SQL. No explanation, no backticks.
- Must be a single SELECT (CTEs allowed, final statement SELECT).
- Do NOT invent tables or columns not present in the schema.
"""

    return llm.generate(system, [{"role": "user", "content": user}]).strip()
