import pandas as pd
import json
from pathlib import Path
import numpy as np

def convert_to_native(obj):
    if isinstance(obj, dict):
        return {k: convert_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native(i) for i in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    else:
        return obj

def identify_category(series):
    dtype = str(series.dtype)
    if pd.api.types.is_numeric_dtype(series):
        if pd.api.types.is_integer_dtype(series) or pd.api.types.is_float_dtype(series):
            return "numeric"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    if series.dtype == "bool":
        return "boolean"
    return "categorical"

def get_numeric_stats(series):
    if series.empty:
        return {"mean": None, "min": None, "max": None, "std": None}
    return {
        "mean": float(round(series.mean(), 2)),
        "min": float(round(series.min(), 2)),
        "max": float(round(series.max(), 2)),
        "std": float(round(series.std(), 2))
    }

def profile_csv(csv_path):
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"File not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    profile = {
        "filename": Path(csv_path).name,
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": [],
        "sample_rows": convert_to_native(df.head(5).to_dict(orient="records"))
    }
    
    for col in df.columns:
        series = df[col]
        category = identify_category(series)
        
        col_info = {
            "name": col,
            "dtype": str(series.dtype),
            "category": category,
            "missing": int(series.isna().sum())
        }
        
        if category == "numeric":
            col_info["stats"] = get_numeric_stats(series)
        elif category == "categorical":
            col_info["unique_values"] = [str(v) for v in series.dropna().unique()[:20]]
            vc = series.value_counts().head(10).to_dict()
            col_info["value_counts"] = {str(k): int(v) for k, v in vc.items()}
        
        profile["columns"].append(col_info)
    
    return profile

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python profiler.py <csv_file>")
        sys.exit(1)
    
    profile = profile_csv(sys.argv[1])
    print(json.dumps(profile, indent=2))
