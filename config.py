import os

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "")

# LLM config
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # 'openai' or 'local'
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "http://localhost:8001/v1/chat/completions")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Misc
MAX_SCHEMA_TABLES = int(os.getenv("MAX_SCHEMA_TABLES", "80"))
MAX_SCHEMA_COLS_PER_TABLE = int(os.getenv("MAX_SCHEMA_COLS_PER_TABLE", "80"))
STRICT_PREFLIGHT = os.getenv("STRICT_PREFLIGHT", "true").lower() == "true"
