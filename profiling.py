import pandas as pd
import numpy as np


def profile_dataframe(df: pd.DataFrame) -> dict:
    """
    Returns a structured profile for the dataframe.

    Returns:
    {
      "dataset": {
        "n_rows": int,
        "n_columns": int,
        "memory_usage_bytes": int,
      },
      "columns": {
        column_name: {
          "pandas_dtype": str,
          "inferred_type": str,
          "non_null_count": int,
          "null_count": int,
          "missing_pct": float,
          "unique_count": int,
          "top_values": [...],
          "numeric_stats": {...} or None,
          "datetime_stats": {...} or None,
          "quality_flags": [],
        },
        ...
      }
    }
    """
    total_rows = len(df)

    profile = {
        "dataset": {
            "n_rows": total_rows,
            "n_columns": len(df.columns),
            "memory_usage_bytes": int(df.memory_usage(deep=True).sum()),
        },
        "columns": {}
    }

    for col_name in df.columns:
        col_profile = _profile_column(df[col_name], col_name, total_rows)
        profile["columns"][col_name] = col_profile

    return profile


def _profile_column(series: pd.Series, col_name: str, total_rows: int) -> dict:
    """Profile a single column and return its metadata."""

    pandas_dtype = str(series.dtype)
    null_count = int(series.isna().sum())
    non_null_count = int(series.notna().sum())
    missing_pct = (null_count / total_rows * 100) if total_rows > 0 else 0.0
    unique_count = int(series.nunique(dropna=True))

    # Infer high-level type
    inferred_type = _infer_type(series, unique_count, total_rows)

    # Get top values
    top_values = _get_top_values(series, n=5)

    # Check for mixed types in object columns
    mixed_types_info = None
    if pandas_dtype == 'object':
        mixed_types_info = _detect_mixed_types(series)

    # Get type-specific statistics
    numeric_stats = None
    datetime_stats = None

    if inferred_type == "numeric":
        numeric_stats = _compute_numeric_stats(series)
    elif inferred_type == "datetime":
        datetime_stats = _compute_datetime_stats(series)

    return {
        "pandas_dtype": pandas_dtype,
        "inferred_type": inferred_type,
        "non_null_count": non_null_count,
        "null_count": null_count,
        "missing_pct": round(missing_pct, 2),
        "unique_count": unique_count,
        "top_values": top_values,
        "numeric_stats": numeric_stats,
        "datetime_stats": datetime_stats,
        "mixed_types_info": mixed_types_info,
        "quality_flags": []
    }


def _infer_type(series: pd.Series, unique_count: int, total_rows: int) -> str:
    """
    Infer high-level type from pandas dtype and column characteristics.

    Returns one of: numeric, datetime, boolean, categorical, text, unknown
    """
    dtype = series.dtype

    # Numeric types
    if pd.api.types.is_numeric_dtype(dtype):
        return "numeric"

    # Datetime types
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "datetime"

    # Boolean types
    if pd.api.types.is_bool_dtype(dtype):
        return "boolean"

    # Object types - need to distinguish categorical from text
    if dtype == 'object':
        # Try to detect datetime strings
        if _is_datetime_column(series):
            return "datetime"

        # Use cardinality heuristic: low uniqueness ratio suggests categorical
        if total_rows > 0:
            unique_ratio = unique_count / total_rows
            if unique_ratio < 0.05:
                return "categorical"
            else:
                return "text"
        else:
            return "unknown"

    return "unknown"


def _is_datetime_column(series: pd.Series) -> bool:
    """
    Check if an object column contains datetime strings.
    Sample up to 100 non-null values for performance.
    """
    non_null_values = series.dropna()
    if len(non_null_values) == 0:
        return False

    # Sample up to 100 values
    sample = non_null_values.head(100)

    try:
        parsed = pd.to_datetime(sample, errors='coerce')
        # If more than 50% parse successfully, consider it datetime
        success_rate = parsed.notna().sum() / len(sample)
        return success_rate > 0.5
    except Exception:
        return False


def _get_top_values(series: pd.Series, n: int = 5) -> list:
    """
    Get top N most frequent values with counts and percentages.
    """
    total_count = len(series)
    if total_count == 0:
        return []

    value_counts = series.value_counts(dropna=False).head(n)

    top_values = []
    for value, count in value_counts.items():
        pct = (count / total_count * 100) if total_count > 0 else 0.0
        top_values.append({
            "value": str(value) if pd.notna(value) else "NULL",
            "count": int(count),
            "pct": round(pct, 2)
        })

    return top_values


def _compute_numeric_stats(series: pd.Series) -> dict:
    """
    Compute statistics for numeric columns.
    """
    try:
        stats = series.describe()
        percentiles = series.quantile([0.25, 0.5, 0.75])

        return {
            "min": float(series.min()) if pd.notna(series.min()) else None,
            "max": float(series.max()) if pd.notna(series.max()) else None,
            "mean": float(stats['mean']) if 'mean' in stats and pd.notna(stats['mean']) else None,
            "median": float(percentiles[0.5]) if pd.notna(percentiles[0.5]) else None,
            "std": float(stats['std']) if 'std' in stats and pd.notna(stats['std']) else None,
            "p25": float(percentiles[0.25]) if pd.notna(percentiles[0.25]) else None,
            "p50": float(percentiles[0.5]) if pd.notna(percentiles[0.5]) else None,
            "p75": float(percentiles[0.75]) if pd.notna(percentiles[0.75]) else None,
        }
    except Exception:
        return None


def _compute_datetime_stats(series: pd.Series) -> dict:
    """
    Compute statistics for datetime columns.
    """
    try:
        # For object columns detected as datetime, convert first
        if series.dtype == 'object':
            series = pd.to_datetime(series, errors='coerce')

        min_date = series.min()
        max_date = series.max()

        return {
            "min": min_date.isoformat() if pd.notna(min_date) else None,
            "max": max_date.isoformat() if pd.notna(max_date) else None,
        }
    except Exception:
        return None


def _detect_mixed_types(series: pd.Series) -> dict:
    """
    Detect if an object column contains mixed Python types.
    Sample up to 100 non-null values for performance.

    Returns dict with:
    - has_mixed_types: bool
    - type_counts: dict of type_name -> count
    - mixed_type_pct: percentage of minority types
    """
    non_null_values = series.dropna()
    if len(non_null_values) == 0:
        return {"has_mixed_types": False, "type_counts": {}, "mixed_type_pct": 0.0}

    # Sample up to 100 values
    sample = non_null_values.head(100)

    # Count types
    type_counts = {}
    for val in sample:
        type_name = type(val).__name__
        type_counts[type_name] = type_counts.get(type_name, 0) + 1

    # Check if mixed
    has_mixed_types = len(type_counts) > 1

    # Calculate percentage of minority types
    mixed_type_pct = 0.0
    if has_mixed_types and len(sample) > 0:
        majority_count = max(type_counts.values())
        minority_count = len(sample) - majority_count
        mixed_type_pct = (minority_count / len(sample)) * 100

    return {
        "has_mixed_types": has_mixed_types,
        "type_counts": type_counts,
        "mixed_type_pct": round(mixed_type_pct, 2)
    }
