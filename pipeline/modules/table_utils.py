# pipeline/modules/table_utils.py
import difflib
from pipeline.modules.validation import validate_tables_and_columns

def correct_tables_and_columns(tables, columns, tables_reference):
    """
    1. Fuzzy-correct table names based on reference.
    2. Filter out invalid tables.
    3. Remap columns to corrected table names.
    4. Ensure proper column quoting via validate_tables_and_columns.
    
    Returns:
        final_tables: List of corrected and valid table names
        final_columns: Dict of table -> list of columns with proper quoting
        corrections: Dict of original_table -> corrected_table
    """
    valid_tables = set(tables_reference["Table_names"].tolist())
    
    # Step 1: Fuzzy correct tables
    corrected_tables = []
    corrections = {}
    for t in tables:
        if t in valid_tables:
            corrected_tables.append(t)
        else:
            close_match = difflib.get_close_matches(t, valid_tables, n=1, cutoff=0.7)
            if close_match:
                corrected_tables.append(close_match[0])
                corrections[t] = close_match[0]

    # Step 2: Only keep valid tables
    final_tables = [t for t in corrected_tables if t in valid_tables]

    # Step 3: Remap columns to corrected table names
    corrected_columns = {}
    for old_table, cols in columns.items():
        new_table = corrections.get(old_table, old_table)
        corrected_columns[new_table] = cols

    # Step 4: Validate tables and columns (quotes etc.)
    final_tables, final_columns = validate_tables_and_columns(final_tables, corrected_columns)

    return final_tables, final_columns, corrections
