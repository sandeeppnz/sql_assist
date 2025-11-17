from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from sql_generator import generate_sql
from sql_validator import (
    is_safe_select,
    has_unknown_tables,
    has_unknown_columns,
    server_preflight_ok,
)
from sql_rewriter import apply_column_mappings
from repair_sql import repair_sql

from db import run_query
from config import STRICT_PREFLIGHT
from sql_utils import extract_sql  # <-- already imported

# ---------------------------------------------------------
# FastAPI Startup
# ---------------------------------------------------------

app = FastAPI(title="SQL Chat Assistant")


class ChatSqlReq(BaseModel):
    question: str
    execute: bool = False
    max_rows: int = 50


class ChatSqlResp(BaseModel):
    sql: str
    executed: bool
    validated: bool
    error: Optional[str] = None
    preview_markdown: Optional[str] = None


MAX_REPAIR_ATTEMPTS = 1


# ---------------------------------------------------------
# Main Endpoint
# ---------------------------------------------------------

@app.post("/chat_sql", response_model=ChatSqlResp)
def chat_sql(req: ChatSqlReq):
    question = req.question.strip()
    execute = req.execute
    max_rows = max(1, min(req.max_rows, 500))

    # -----------------------------------------------------
    # 1) Generate SQL from natural-language question
    # -----------------------------------------------------
    raw_sql = generate_sql(question)
    # 🔑 Normalize here so everything downstream sees *clean* SQL
    sql = extract_sql(raw_sql)

    # -----------------------------------------------------
    # 2) Safety: must be SELECT/CTE and contain no DDL/DML
    # -----------------------------------------------------
    if not is_safe_select(sql):
        return ChatSqlResp(
            sql=sql,
            executed=False,
            validated=False,
            error="Blocked: generated SQL is not a safe SELECT statement.",
        )

    # -----------------------------------------------------
    # 3) Apply column/table mappings (e.g., fix missing columns)
    # -----------------------------------------------------
    rewritten_sql, changed = apply_column_mappings(sql)
    if changed:
        sql = rewritten_sql

    # -----------------------------------------------------
    # 4) Table-level validation
    # -----------------------------------------------------
    has_bad_tables, bad_tables = has_unknown_tables(sql)
    if has_bad_tables:
        return ChatSqlResp(
            sql=sql,
            executed=False,
            validated=False,
            error=f"Query referenced unknown tables: {', '.join(bad_tables)}"
        )

    # -----------------------------------------------------
    # 5) Column-level validation
    # -----------------------------------------------------
    has_bad_cols, bad_cols = has_unknown_columns(sql)
    if has_bad_cols:
        pretty = [f"{tbl}.{col} (alias {alias})" for (tbl, alias, col) in bad_cols]
        return ChatSqlResp(
            sql=sql,
            executed=False,
            validated=False,
            error="Query referenced unknown columns: " + ", ".join(pretty)
        )

    # -----------------------------------------------------
    # 6) SQL Server Preflight (compile-only)
    # -----------------------------------------------------
    ok, msg = server_preflight_ok(sql) if STRICT_PREFLIGHT else (True, "ok")
    attempts = 0

    # Attempt LLM repair if preflight fails
    while not ok and attempts < MAX_REPAIR_ATTEMPTS:
        attempts += 1

        repaired_raw = repair_sql(question, sql, msg)
        # 🔑 Normalize repaired SQL as well
        repaired = extract_sql(repaired_raw)

        if not is_safe_select(repaired):
            break

        # Validate repaired table list
        has_bad_tables, bad_tables = has_unknown_tables(repaired)
        if has_bad_tables:
            break

        # Validate repaired columns
        has_bad_cols, bad_cols = has_unknown_columns(repaired)
        if has_bad_cols:
            break

        sql = repaired
        ok, msg = server_preflight_ok(sql) if STRICT_PREFLIGHT else (True, "ok")

    if not ok:
        return ChatSqlResp(
            sql=sql,
            executed=False,
            validated=False,
            error=f"Preflight failed; could not generate valid SQL.\n\n{msg}",
        )

    # -----------------------------------------------------
    # 7) SQL validated successfully → return or execute
    # -----------------------------------------------------
    if not execute:
        return ChatSqlResp(
            sql=sql,
            executed=False,
            validated=True,
            error=None,
        )

    # -----------------------------------------------------
    # 8) Execute the query
    # -----------------------------------------------------
    try:
        df = run_query(sql)
        preview = df.head(max_rows).to_markdown(index=False)

        return ChatSqlResp(
            sql=sql,
            executed=True,
            validated=True,
            error=None,
            preview_markdown=preview,
        )
    except Exception as ex:
        return ChatSqlResp(
            sql=sql,
            executed=False,
            validated=True,
            error=f"Execution failed: {ex}",
            preview_markdown=None,
        )


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@app.get("/")
def health():
    return {"ok": True, "message": "SQL Chat Assistant is running."}
