# data/

Place your SQL schema DDL files here, for example exported CREATE TABLE scripts.

These are not parsed programmatically, but their text is appended to the LLM schema
context to help it choose the correct tables and columns.

The authoritative source of schema is still the live DB via SQLAlchemy introspection.
