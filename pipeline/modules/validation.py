# pipeline/modules/validation.py
import difflib

def correct_tables(tables, tables_reference):
    """
    Ensure all table names are valid against tables_reference.
    If a table is invalid, try fuzzy correction.
    """
    valid_tables = set(tables_reference["Table_names"].tolist())
    corrected_tables = []
    corrections = {}

    for t in tables:
        if t in valid_tables:
            corrected_tables.append(t)
        else:
            # Try fuzzy correction
            close_match = difflib.get_close_matches(t, valid_tables, n=1, cutoff=0.7)
            if close_match:
                corrected_tables.append(close_match[0])
                corrections[t] = close_match[0]
            else:
                # Drop if no close match
                print(f"[DEBUG] Dropping invalid table: {t}")

    if corrections:
        print(f"[DEBUG] Corrected tables: {corrections}")

    return corrected_tables,corrections

def validate_tables_and_columns(tables, columns, corrections=None):
    """
    Tables: remove quotes if present.
    Columns: wrap with double quotes only if not already quoted.
    Also remap columns to corrected tables if corrections dict is provided.
    """
    # Tables cleaning
    cleaned_tables = []
    for t in tables:
        t = t.strip()
        if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
            cleaned_tables.append(t[1:-1])  # remove quotes
        else:
            cleaned_tables.append(t)

    # Columns cleaning & remapping
    cleaned_columns = {}
    for tbl, cols in columns.items():
        # Remap table if corrections exist
        new_tbl = corrections.get(tbl, tbl) if corrections else tbl

        cleaned_cols = []
        for c in cols:
            c = c.strip()
            if (c.startswith('"') and c.endswith('"')) or (c.startswith("'") and c.endswith("'")):
                cleaned_cols.append(c)  # already quoted, keep as-is
            else:
                cleaned_cols.append(f'"{c}"')  # wrap with double quotes

        cleaned_columns[new_tbl] = cleaned_cols

    return cleaned_tables, cleaned_columns
