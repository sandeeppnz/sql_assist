#!/usr/bin/env python

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from dotenv import load_dotenv

# Load env like app.py
load_dotenv()

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
from sql_utils import extract_sql  # 🔑 NEW: use same extractor as app.py


MAX_REPAIR_ATTEMPTS = 1


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def execute_sql(sql: str) -> Tuple[bool, Any, str | None]:
    """
    Execute SQL and return (ok, df_or_none, error_or_none).
    Uses db.run_query(), which should return a pandas DataFrame.
    """
    try:
        df = run_query(sql)
        return True, df, None
    except Exception as ex:
        return False, None, str(ex)


def compare_results(gold_df, model_df) -> bool:
    """
    Compare two result DataFrames.

    Current strategy:
      - if shapes differ: no match
      - if column sets differ: no match
      - otherwise reorder columns to gold_df's order,
        reset index and use DataFrame.equals()

    Adjust if you want looser comparison.
    """
    if gold_df is None or model_df is None:
        return False

    try:
        # Shape check
        if gold_df.shape != model_df.shape:
            return False

        # Column set check
        if set(gold_df.columns) != set(model_df.columns):
            return False

        # Align column order
        model_df = model_df[gold_df.columns]

        # Reset index and compare
        g = gold_df.reset_index(drop=True)
        m = model_df.reset_index(drop=True)
        return g.equals(m)
    except Exception:
        return False


def eval_one_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate a single gold record against the current pipeline.

    Expected keys in rec (some may be missing initially):
      - id               (optional, for logging)
      - question         (required)
      - gold_sql         (required)
      - model_sql        (will be overwritten)
      - validated        (updated)
      - model_exec_ok    (updated)
      - result_match     (updated)
      - gold_error       (updated)
      - model_error      (updated)
    """
    rec_id = rec.get("id", "?")
    question = rec["question"]
    gold_sql = rec["gold_sql"]

    print(f"\n=== Evaluating ID {rec_id}: {question} ===")

    # -----------------------------------------------------
    # 1) Execute gold_sql
    # -----------------------------------------------------
    gold_ok, gold_df, gold_err = execute_sql(gold_sql)
    rec["gold_error"] = gold_err

    if gold_ok:
        print("  ✓ Gold SQL executed OK.")
    else:
        print("  ✗ Gold SQL FAILED:")
        print("    ", gold_err)

    # -----------------------------------------------------
    # 2) Generate model SQL from question
    # -----------------------------------------------------
    model_sql_raw = generate_sql(question)
    # 🔑 Normalize LLM output to bare SQL (strip fences, explanation, etc.)
    model_sql = extract_sql(model_sql_raw)
    rec["model_sql"] = model_sql

    print("  Model SQL generated:")
    print("    " + model_sql.replace("\n", "\n    "))

    # -----------------------------------------------------
    # 3) Safety: must be SELECT/CTE and no DDL/DML
    # -----------------------------------------------------
    if not is_safe_select(model_sql):
        rec["validated"] = False
        rec["model_exec_ok"] = False
        rec["result_match"] = False
        rec["model_error"] = "not a safe SELECT statement"
        print("  ✗ Not a safe SELECT; skipping.")
        return rec

    # -----------------------------------------------------
    # 4) Logical → physical column mapping
    # -----------------------------------------------------
    rewritten_sql, changed = apply_column_mappings(model_sql)
    if changed:
        model_sql = rewritten_sql
        rec["model_sql"] = model_sql
        print("  Column mappings applied.")

    # -----------------------------------------------------
    # 5) Unknown table validation
    # -----------------------------------------------------
    has_bad_tables, bad_tables = has_unknown_tables(model_sql)
    if has_bad_tables:
        msg = "Unknown tables: " + ", ".join(bad_tables)
        rec["validated"] = False
        rec["model_exec_ok"] = False
        rec["result_match"] = False
        rec["model_error"] = msg
        print("  ✗", msg)
        return rec

    # -----------------------------------------------------
    # 6) Unknown column validation
    # -----------------------------------------------------
    has_bad_cols, bad_cols = has_unknown_columns(model_sql)
    if has_bad_cols:
        pretty = [f"{tbl}.{col} (alias {alias})" for (tbl, alias, col) in bad_cols]
        msg = "Unknown columns: " + ", ".join(pretty)
        rec["validated"] = False
        rec["model_exec_ok"] = False
        rec["result_match"] = False
        rec["model_error"] = msg
        print("  ✗", msg)
        return rec

    # -----------------------------------------------------
    # 7) SQL Server preflight (compile-only) with repair loop
    # -----------------------------------------------------
    ok, msg = server_preflight_ok(model_sql) if STRICT_PREFLIGHT else (True, "ok")
    attempts = 0

    while not ok and attempts < MAX_REPAIR_ATTEMPTS:
        attempts += 1
        print("  Preflight failed; attempting repair...")

        repaired_raw = repair_sql(question, model_sql, msg)
        # 🔑 Normalize repaired SQL as well
        repaired = extract_sql(repaired_raw)

        if not is_safe_select(repaired):
            print("  ✗ Repaired SQL not a safe SELECT; aborting repair.")
            break

        # Validate repaired tables
        has_bad_tables, bad_tables = has_unknown_tables(repaired)
        if has_bad_tables:
            print("  ✗ Repaired SQL has unknown tables:", ", ".join(bad_tables))
            break

        # Validate repaired columns
        has_bad_cols, bad_cols = has_unknown_columns(repaired)
        if has_bad_cols:
            pretty = [f"{tbl}.{col} (alias {alias})" for (tbl, alias, col) in bad_cols]
            print("  ✗ Repaired SQL has unknown columns:", ", ".join(pretty))
            break

        model_sql = repaired
        rec["model_sql"] = model_sql
        print("  Repair produced new SQL.")
        ok, msg = server_preflight_ok(model_sql) if STRICT_PREFLIGHT else (True, "ok")

    if not ok:
        rec["validated"] = False
        rec["model_exec_ok"] = False
        rec["result_match"] = False
        rec["model_error"] = f"Preflight failed after repair attempts: {msg}"
        print("  ✗ Preflight failed; giving up.")
        return rec

    # If we got here, validation succeeded
    rec["validated"] = True
    rec["model_error"] = None
    print("  ✓ SQL validated successfully.")

    # -----------------------------------------------------
    # 8) Execute model SQL
    # -----------------------------------------------------
    model_ok, model_df, model_err = execute_sql(model_sql)
    rec["model_exec_ok"] = model_ok
    rec["model_error"] = model_err

    if not model_ok:
        print("  ✗ Model SQL execution FAILED:")
        print("    ", model_err)
        rec["result_match"] = False
        return rec

    print("  ✓ Model SQL executed OK.")

    # -----------------------------------------------------
    # 9) Compare results if gold executed OK as well
    # -----------------------------------------------------
    if gold_ok and model_ok:
        match = compare_results(gold_df, model_df)
        rec["result_match"] = match
        print("  Result match:", "✓" if match else "✗")
    else:
        rec["result_match"] = False
        print("  Skipping result comparison (at least one side failed).")

    return rec


# ---------------------------------------------------------
# Main CLI
# ---------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate gold SQL questions.")
    parser.add_argument(
        "--input",
        type=str,
        default="gold_eval.json",
        help="Path to input gold JSON file (list of records).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="gold_eval_results.json",
        help="Path to output JSON file with updated records.",
    )

    args = parser.parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    print(f"Loading gold records from {input_path} ...")
    with input_path.open("r", encoding="utf-8") as f:
        data: List[Dict[str, Any]] = json.load(f)

    total = len(data)
    print(f"Loaded {total} records.")

    updated: List[Dict[str, Any]] = []
    match_count = 0
    valid_count = 0
    exec_ok_count = 0

    for rec in data:
        rec = eval_one_record(rec)
        updated.append(rec)

        if rec.get("validated"):
            valid_count += 1
        if rec.get("model_exec_ok"):
            exec_ok_count += 1
        if rec.get("result_match"):
            match_count += 1

    print("\n=== Summary ===")
    print(f"Total records:            {total}")
    print(f"Validated (model):        {valid_count}")
    print(f"Executed OK (model):      {exec_ok_count}")
    print(f"Result matches (gold vs): {match_count}")

    print(f"\nWriting updated results to {output_path} ...")
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(updated, f, indent=2)

    print("Done.")


if __name__ == "__main__":
    main()
