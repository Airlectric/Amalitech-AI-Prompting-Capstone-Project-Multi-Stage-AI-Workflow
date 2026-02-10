import pandas as pd
import json
from pathlib import Path

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
    return {
        "mean": round(series.mean(), 2) if not series.empty else None,
        "min": round(series.min(), 2) if not series.empty else None,
        "max": round(series.max(), 2) if not series.empty else None,
        "std": round(series.std(), 2) if not series.empty else None
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
        "sample_rows": df.head(5).to_dict(orient="records")
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
            col_info["unique_values"] = list(series.dropna().unique()[:20])
            col_info["value_counts"] = series.value_counts().head(10).to_dict()
        
        profile["columns"].append(col_info)
    
    return profile

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python profiler.py <csv_file>")
        sys.exit(1)
    
    profile = profile_csv(sys.argv[1])
    print(json.dumps(profile, indent=2))
