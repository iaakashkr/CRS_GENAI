# joining_instructions.py

import pandas as pd
from typing import List, Dict, Any

CSV_FILE_PATH = 'crs_joining_instructions.csv'

def get_joining_instructions(table_names: List[str]) -> List[Dict[str, Any]]:
    """
    Returns joining instructions as a list of dicts suitable for generate_sql_from_dto.
    Each dict has: from_table, to_table, instruction.
    """
    # Load CSV
    df = pd.read_csv(CSV_FILE_PATH, index_col=0)
    df.index = df.index.str.lower()
    df.columns = df.columns.str.lower()

    # Flatten table list if any nested lists and lowercase
    table_list = []
    for t in table_names:
        if isinstance(t, list):
            t = t[0]
        table_list.append(t.lower())

    # Filter only tables present in CSV
    valid_tables = [t for t in table_list if t in df.index]
    if not valid_tables:
        return []

    filtered_df = df.loc[valid_tables, valid_tables]

    joinings: List[Dict[str, Any]] = []

    for from_table in valid_tables:
        for to_table in filtered_df.columns:
            if from_table == to_table:
                continue  # skip self-join
            instr = filtered_df.at[from_table, to_table]
            if pd.notna(instr) and instr.strip().upper() != "NA" and instr.strip() != "":
                joinings.append({
                    "from_table": from_table,
                    "to_table": to_table,
                    "instruction": instr.strip()
                })

    # Optional: sort for deterministic order
    joinings.sort(key=lambda x: (x["from_table"], x["to_table"]))

    return joinings
