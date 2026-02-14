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
    elif pd.isna(obj):
        return None
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

def calculate_skewness(series):
    try:
        n = len(series)
        if n < 3:
            return None
        mean = series.mean()
        std = series.std()
        if std == 0:
            return None
        return float(((series - mean) ** 3).sum() / (n * std ** 3))
    except:
        return None

def calculate_kurtosis(series):
    try:
        n = len(series)
        if n < 4:
            return None
        mean = series.mean()
        std = series.std()
        if std == 0:
            return None
        return float(((series - mean) ** 4).sum() / (n * std ** 4)) - 3
    except:
        return None

def get_numeric_stats(series):
    if series.empty or series.dropna().empty:
        return {
            "count": 0,
            "null_count": int(series.isna().sum()),
            "null_percentage": 100.0 if len(series) > 0 else 0.0,
            "mean": None,
            "median": None,
            "mode": None,
            "min": None,
            "max": None,
            "range": None,
            "variance": None,
            "std": None,
            "coefficient_of_variation": None,
            "skewness": None,
            "kurtosis": None,
            "percentile_25": None,
            "percentile_50": None,
            "percentile_75": None,
            "iqr": None
        }
    
    clean_series = series.dropna()
    n = len(clean_series)
    null_count = int(series.isna().sum())
    null_percentage = round((null_count / len(series)) * 100, 2) if len(series) > 0 else 0.0
    
    mean_val = clean_series.mean()
    median_val = clean_series.median()
    
    try:
        mode_val = clean_series.mode()
        if len(mode_val) > 0:
            mode_val = float(mode_val.iloc[0])
        else:
            mode_val = float(clean_series.iloc[0])
    except:
        mode_val = None
    
    min_val = clean_series.min()
    max_val = clean_series.max()
    range_val = float(max_val - min_val)
    variance_val = float(clean_series.var())
    std_val = float(clean_series.std())
    
    cv = (std_val / mean_val * 100) if mean_val and mean_val != 0 else None
    
    skewness_val = calculate_skewness(clean_series)
    kurtosis_val = calculate_kurtosis(clean_series)
    
    try:
        percentile_25 = float(clean_series.quantile(0.25))
        percentile_50 = float(clean_series.quantile(0.50))
        percentile_75 = float(clean_series.quantile(0.75))
        iqr_val = percentile_75 - percentile_25
    except:
        percentile_25 = None
        percentile_50 = None
        percentile_75 = None
        iqr_val = None
    
    return {
        "count": n,
        "null_count": null_count,
        "null_percentage": null_percentage,
        "mean": round(float(mean_val), 2) if mean_val is not None else None,
        "median": round(float(median_val), 2) if median_val is not None else None,
        "mode": round(float(mode_val), 2) if mode_val is not None else None,
        "min": round(float(min_val), 2) if min_val is not None else None,
        "max": round(float(max_val), 2) if max_val is not None else None,
        "range": round(range_val, 2),
        "variance": round(variance_val, 2) if variance_val is not None else None,
        "std": round(std_val, 2) if std_val is not None else None,
        "coefficient_of_variation": round(cv, 2) if cv is not None else None,
        "skewness": round(skewness_val, 2) if skewness_val is not None else None,
        "kurtosis": round(kurtosis_val, 2) if kurtosis_val is not None else None,
        "percentile_25": round(percentile_25, 2) if percentile_25 is not None else None,
        "percentile_50": round(percentile_50, 2) if percentile_50 is not None else None,
        "percentile_75": round(percentile_75, 2) if percentile_75 is not None else None,
        "iqr": round(iqr_val, 2) if iqr_val is not None else None
    }

def get_categorical_stats(series):
    if series.empty or series.dropna().empty:
        return {
            "count": 0,
            "null_count": int(series.isna().sum()),
            "null_percentage": 100.0 if len(series) > 0 else 0.0,
            "unique_count": 0,
            "unique_values": [],
            "value_counts": {},
            "mode": None,
            "mode_frequency": None,
            "mode_percentage": None
        }
    
    clean_series = series.dropna()
    n = len(clean_series)
    null_count = int(series.isna().sum())
    null_percentage = round((null_count / len(series)) * 100, 2) if len(series) > 0 else 0.0
    
    unique_values = [str(v) for v in clean_series.unique()[:10]]
    unique_count = len(clean_series.unique())

    vc = clean_series.value_counts()
    value_counts = {str(k): int(v) for k, v in vc.head(5).items()}
    
    mode_val = str(vc.index[0]) if len(vc) > 0 else None
    mode_frequency = int(vc.iloc[0]) if len(vc) > 0 else 0
    mode_percentage = round((mode_frequency / n) * 100, 2) if n > 0 else 0.0
    
    return {
        "count": n,
        "null_count": null_count,
        "null_percentage": null_percentage,
        "unique_count": unique_count,
        "unique_values": unique_values,
        "value_counts": value_counts,
        "mode": mode_val,
        "mode_frequency": mode_frequency,
        "mode_percentage": mode_percentage
    }

MAX_PROFILE_ROWS = 2000

def profile_csv(csv_path):
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"File not found: {csv_path}")

    df_full = pd.read_csv(csv_path)
    total_rows = len(df_full)
    total_nulls = int(df_full.isna().sum().sum())

    # Sample a representative subset for profiling — the AI only needs
    # approximate statistics to plan the analysis, not exact figures from
    # every row.  The generated code still runs against the full dataset.
    if total_rows > MAX_PROFILE_ROWS:
        df = df_full.sample(n=MAX_PROFILE_ROWS, random_state=42)
    else:
        df = df_full

    profile = {
        "filename": Path(csv_path).name,
        "row_count": total_rows,
        "column_count": len(df.columns),
        "profiled_rows": len(df),
        "total_null_values": total_nulls,
        "columns": [],
        "sample_rows": convert_to_native(df_full.head(3).to_dict(orient="records"))
    }

    for col in df.columns:
        series = df[col]
        category = identify_category(series)

        col_info = {
            "name": col,
            "dtype": str(series.dtype),
            "category": category
        }

        if category == "numeric":
            col_info["stats"] = get_numeric_stats(series)
        elif category == "categorical":
            col_info["stats"] = get_categorical_stats(series)
        else:
            col_info["stats"] = {
                "count": len(series.dropna()),
                "null_count": int(series.isna().sum()),
                "null_percentage": round((series.isna().sum() / len(series)) * 100, 2) if len(series) > 0 else 0.0
            }

        profile["columns"].append(col_info)

    return profile

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python profiler.py <csv_file>")
        sys.exit(1)
    
    profile = profile_csv(sys.argv[1])
    print(json.dumps(profile, indent=2))
