# import csv
# import os
# import uuid
# from datetime import datetime

# AUDIT_DIR = "audit_logs"
# os.makedirs(AUDIT_DIR, exist_ok=True)

# def flatten_pipeline_result(result: dict):
#     """
#     Flatten pipeline result for Excel-friendly CSV.
#     - Splits intent dict into separate columns
#     - Splits token_usage dict into separate columns
#     """
#     base = {
#         "original_question": result.get("original_question", ""),
#         "rephrased_question": result.get("rephrased_question", ""),
#         "selected_tables": str(result.get("selected_tables", "")),
#         "selected_columns": str(result.get("selected_columns", "")),
#         "sql_query": result.get("sql_query", "")
#     }

#     # Flatten intent
#     intent = result.get("intent", {})
#     if isinstance(intent, dict):
#         for k, v in intent.items():
#             base[f"intent_{k}"] = v
#     else:
#         base["intent"] = str(intent)

#     # Flatten token_usage
#     usage = result.get("usage", {})
#     if isinstance(usage, dict):
#         for key, value in usage.items():
#             if isinstance(value, dict):
#                 for subkey, subval in value.items():
#                     base[f"{key}_{subkey}"] = subval
#             else:
#                 base[key] = value
#     else:
#         base["token_usage"] = str(usage)

#     return base

# def save_pipeline_result_with_id(result: dict, filename: str = None):
#     """
#     Save pipeline result to CSV dynamically with run_id and timestamp:
#     - Each SQL row becomes one CSV row
#     - Metadata + flattened intent + flattened token usage
#     - Works for any SQL query columns
#     - Adds unique run_id and timestamp for audit tracking
#     """
#     run_id = str(uuid.uuid4())  # unique identifier for this pipeline run
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     if filename is None:
#         filename = f"pipeline_audit.csv"  # append to same file for multiple runs
#     filepath = os.path.join(AUDIT_DIR, filename)

#     sql_rows = result.get("sql_result", [])
#     if not sql_rows:
#         sql_rows = [{}]  # ensure at least one row

#     rows_to_write = []
#     for sql_row in sql_rows:
#         flat_base = flatten_pipeline_result(result)
#         # Add SQL row fields
#         for k, v in sql_row.items():
#             flat_base[k] = v
#         # Add run_id and timestamp
#         flat_base["run_id"] = run_id
#         flat_base["timestamp"] = timestamp
#         rows_to_write.append(flat_base)

#     # Dynamically get all columns
#     fieldnames = set()
#     for row in rows_to_write:
#         fieldnames.update(row.keys())
#     fieldnames = list(fieldnames)

#     # Write CSV
#     write_header = not os.path.isfile(filepath)
#     with open(filepath, mode="a", newline="", encoding="utf-8") as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         if write_header:
#             writer.writeheader()
#         writer.writerows(rows_to_write)

#     print(f"✅ Pipeline result saved to audit CSV with run_id: {filepath}")

#--------------------working_________________________________________________________________________________


import csv
import os
import uuid
import time
from datetime import datetime

AUDIT_DIR = "audit_logs"
os.makedirs(AUDIT_DIR, exist_ok=True)

MASTER_FILE = os.path.join(AUDIT_DIR, "monitor_master.csv")
CHILD_FILE = os.path.join(AUDIT_DIR, "monitor_child.csv")


def save_master_record(username, question, response, intent, sql_query, tokens, start_time, end_time, status=True,child_steps_total=0):#chnage
    """Save summary info per pipeline run."""
    fieldnames = [
        "id", "username", "request", "response", "status", "intent", "query",
        "prompt_tokens", "completion_tokens", "total_tokens",
        "start_time", "end_time", "time_taken_in_seconds"
    ]

    # Generate new ID
    if os.path.exists(MASTER_FILE):
        with open(MASTER_FILE, "r", encoding="utf-8") as f:
            try:
                last_id = max(int(row.split(",")[0]) for row in f.readlines()[1:])  # skip header
            except ValueError:
                last_id = 0
    else:
        last_id = 0

    run_id = last_id + 1
    time_taken = end_time - start_time

    total_tokens = child_steps_total if child_steps_total else tokens.get("total_tokens", 0)#chnage


    row = {
        "id": run_id,
        "username": username,
        "request": question,
        "response": response,
        "status": status,
        "intent": intent,
        "query": sql_query,
        "prompt_tokens": tokens.get("prompt_tokens", 0),
        "completion_tokens": tokens.get("completion_tokens", 0),
        "total_tokens": total_tokens, #chnage
        "start_time": start_time,
        "end_time": end_time,
        "time_taken_in_seconds": time_taken
    }

    write_header = not os.path.exists(MASTER_FILE)
    with open(MASTER_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)

    return run_id


def save_child_records(master_id, steps_usage):
    """
    Save stepwise metrics linked to master run.
    steps_usage: list of dicts like
        [{"step": "intent_identification", "prompt_tokens": 123, "completion_tokens": 2, "start_time": t0, "end_time": t1}, ...]
    """
    fieldnames = ["id", "type", "master_id", "prompt_tokens", "completion_tokens", "total_tokens", "start_time", "end_time", "time_taken_in_seconds"]

    if os.path.exists(CHILD_FILE):
        with open(CHILD_FILE, "r", encoding="utf-8") as f:
            try:
                last_id = max(int(row.split(",")[0]) for row in f.readlines()[1:])
            except ValueError:
                last_id = 0
    else:
        last_id = 0

    rows = []
    for step in steps_usage:
        last_id += 1
        total_tokens = step.get("prompt_tokens", 0) + step.get("completion_tokens", 0)
        time_taken = step.get("end_time", 0) - step.get("start_time", 0)
        row = {
            "id": last_id,
            "type": step.get("step"),
            "master_id": master_id,
            "prompt_tokens": step.get("prompt_tokens", 0),
            "completion_tokens": step.get("completion_tokens", 0),
            "total_tokens": total_tokens,
            "start_time": step.get("start_time", 0),
            "end_time": step.get("end_time", 0),
            "time_taken_in_seconds": time_taken
        }
        rows.append(row)

    write_header = not os.path.exists(CHILD_FILE)
    with open(CHILD_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)
