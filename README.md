# SQL Chat Assistant (LLM + SQL Server)

This is a minimal reference implementation of a **safe SQL assistant**:

- User asks a natural-language question
- LLM generates **one T-SQL SELECT**
- We run strict validation:
  - Only SELECT/CTE allowed
  - Tables must exist in the schema
  - SQL Server preflight via `sp_describe_first_result_set`
- Optional **auto-repair** using the SQL Server error message
- Optional **execution** controlled via `execute` flag

## Project structure

- `app.py` – FastAPI app and `/chat_sql` endpoint
- `schema_service.py` – loads DB schema (and optional `.sql` files from `data/`)
- `sql_generator.py` – LLM call: question → SQL
- `sql_validator.py` – safety and preflight checks
- `repair_sql.py` – simple auto-repair using the DB error
- `llm.py` – provider-agnostic LLM wrapper (OpenAI or local HTTP)
- `db.py` – SQLAlchemy engine + `run_query`
- `config.py` – environment-driven config
- `data/` – put your schema `.sql` files here for extra context

## Quick start

1. Create and activate a virtual env.
2. Install requirements:

   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables (example):

   ```bash
   export DATABASE_URL='mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server'
   export LLM_PROVIDER='openai'          # or 'local'
   export LLM_MODEL='gpt-4.1-mini'
   export OPENAI_API_KEY='sk-...'
   ```

4. Run the API:

   ```bash
   uvicorn app:app --reload
   ```

5. Call the endpoint:

   ```bash
   curl -X POST http://localhost:8000/chat_sql \
     -H "Content-Type: application/json" \
     -d '{"question": "Top 5 customers by InvoiceTotal last 30 days", "execute": false}'
   ```

Set `"execute": true` to actually run the SQL on SQL Server.
