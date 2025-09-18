import pandas as pd
import chardet

def detect_encoding(file_path: str) -> str:
    """Detect encoding of a file."""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
    return result['encoding']

def load_csv(file_path: str) -> pd.DataFrame:
    """Load CSV with detected encoding."""
    encoding = detect_encoding(file_path)
    return pd.read_csv(file_path, encoding=encoding)

def load_references(
    metrics_path: str = "crs_metrics.csv",
    columns_path: str = "crs_columns.csv",
    tables_path: str = "crs_tables.csv"
):
    """Load all reference CSVs and return them as DataFrames."""
    metrics_reference = load_csv(metrics_path)
    columns_reference = load_csv(columns_path)
    tables_reference = load_csv(tables_path)

    return metrics_reference, columns_reference, tables_reference
