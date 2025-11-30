import pandas as pd
import numpy as np
import string


# Common placeholder values for string quality detection
COMMON_PLACEHOLDERS = {
    'n/a', 'na', 'null', 'none', 'unknown', 'tbd', 'pending',
    'not available', 'not applicable', '#n/a', 'nan', 'nil',
    '', ' ', '--', '?', 'missing', 'n.a.', 'n.a', 'n\\a'
}


def profile_dataframe(df: pd.DataFrame) -> dict:
    """
    Returns a structured profile for the dataframe.

    Returns:
    {
      "dataset": {
        "n_rows": int,
        "n_columns": int,
        "memory_usage_bytes": int,
        "duplicate_analysis": {...},
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
          "string_quality": {...} or None,
          "quality_flags": [],
        },
        ...
      }
    }
    """
    total_rows = len(df)

    # Analyze duplicates at dataset level
    duplicate_analysis = _analyze_duplicates(df)

    profile = {
        "dataset": {
            "n_rows": total_rows,
            "n_columns": len(df.columns),
            "memory_usage_bytes": int(df.memory_usage(deep=True).sum()),
            "duplicate_analysis": duplicate_analysis,
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
    string_quality = None

    if inferred_type == "numeric":
        numeric_stats = _compute_numeric_stats(series)
    elif inferred_type == "datetime":
        datetime_stats = _compute_datetime_stats(series)

    # Analyze string quality for text/categorical columns
    if inferred_type in ["text", "categorical"]:
        string_quality = _analyze_string_quality(series)

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
        "string_quality": string_quality,
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

        # Distribution pattern metrics
        skewness = series.skew()
        zero_count = int((series == 0).sum())
        zero_pct = (zero_count / len(series)) * 100 if len(series) > 0 else 0.0
        negative_count = int((series < 0).sum())
        negative_pct = (negative_count / len(series)) * 100 if len(series) > 0 else 0.0

        return {
            "min": float(series.min()) if pd.notna(series.min()) else None,
            "max": float(series.max()) if pd.notna(series.max()) else None,
            "mean": float(stats['mean']) if 'mean' in stats and pd.notna(stats['mean']) else None,
            "median": float(percentiles[0.5]) if pd.notna(percentiles[0.5]) else None,
            "std": float(stats['std']) if 'std' in stats and pd.notna(stats['std']) else None,
            "p25": float(percentiles[0.25]) if pd.notna(percentiles[0.25]) else None,
            "p50": float(percentiles[0.5]) if pd.notna(percentiles[0.5]) else None,
            "p75": float(percentiles[0.75]) if pd.notna(percentiles[0.75]) else None,
            "skewness": float(skewness) if pd.notna(skewness) else None,
            "zero_count": zero_count,
            "zero_pct": round(zero_pct, 2),
            "negative_count": negative_count,
            "negative_pct": round(negative_pct, 2),
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

        # Future date detection
        current_date = pd.Timestamp.now()
        future_mask = series > current_date
        future_count = int(future_mask.sum())
        future_pct = (future_count / len(series)) * 100 if len(series) > 0 else 0.0
        max_future_date = series[future_mask].max() if future_count > 0 else None

        return {
            "min": min_date.isoformat() if pd.notna(min_date) else None,
            "max": max_date.isoformat() if pd.notna(max_date) else None,
            "future_count": future_count,
            "future_pct": round(future_pct, 2),
            "max_future_date": max_future_date.isoformat() if pd.notna(max_future_date) else None,
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


def _analyze_string_quality(series: pd.Series, max_sample: int = 1000) -> dict:
    """
    Analyze string quality issues for text/categorical columns.

    Args:
        series: Pandas Series to analyze
        max_sample: Maximum rows to sample (for performance on large datasets)

    Returns:
        dict with string quality metrics, or None if not object dtype
    """
    # Only analyze object columns
    if series.dtype != 'object':
        return None

    # Get non-null values
    non_null = series.dropna()
    if len(non_null) == 0:
        return {
            "whitespace_count": 0,
            "whitespace_pct": 0.0,
            "placeholder_count": 0,
            "placeholder_pct": 0.0,
            "placeholder_values": [],
            "casing_issues": False,
            "casing_groups": 0,
            "special_char_count": 0,
            "special_char_pct": 0.0,
        }

    # Sample for performance
    sample = non_null if len(non_null) <= max_sample else non_null.sample(n=max_sample, random_state=42)
    total_analyzed = len(sample)
    str_series = sample.astype(str)

    # 1. WHITESPACE: Leading/trailing spaces
    whitespace_mask = str_series.str.len() != str_series.str.strip().str.len()
    whitespace_count = int(whitespace_mask.sum())
    whitespace_pct = (whitespace_count / total_analyzed * 100) if total_analyzed > 0 else 0.0

    # 2. PLACEHOLDERS: Common placeholder values
    lower_stripped = str_series.str.lower().str.strip()
    placeholder_mask = lower_stripped.isin(COMMON_PLACEHOLDERS)
    placeholder_count = int(placeholder_mask.sum())
    placeholder_pct = (placeholder_count / total_analyzed * 100) if total_analyzed > 0 else 0.0
    placeholder_values = lower_stripped[placeholder_mask].unique().tolist()[:5]

    # 3. CASING ISSUES: Same value with different cases
    lowercased = str_series.str.lower()
    value_counts = lowercased.value_counts()
    casing_issues = False
    casing_groups = 0

    for lower_val in value_counts.index:
        matches = str_series[lowercased == lower_val].unique()
        if len(matches) > 1:
            casing_issues = True
            casing_groups += 1

    # 4. SPECIAL CHARACTERS: Non-printable characters
    printable = set(string.printable)
    special_char_mask = str_series.apply(lambda s: any(c not in printable for c in str(s)))
    special_char_count = int(special_char_mask.sum())
    special_char_pct = (special_char_count / total_analyzed * 100) if total_analyzed > 0 else 0.0

    return {
        "whitespace_count": whitespace_count,
        "whitespace_pct": round(whitespace_pct, 2),
        "placeholder_count": placeholder_count,
        "placeholder_pct": round(placeholder_pct, 2),
        "placeholder_values": placeholder_values,
        "casing_issues": casing_issues,
        "casing_groups": casing_groups,
        "special_char_count": special_char_count,
        "special_char_pct": round(special_char_pct, 2),
    }


def _collect_examples(series: pd.Series, condition_mask: pd.Series, max_examples: int = 5) -> list:
    """
    Collect example values that match a condition.

    Args:
        series: The column data
        condition_mask: Boolean mask indicating which values match condition
        max_examples: Maximum number of examples to collect

    Returns:
        List of example dicts with row_number and value
    """
    examples = []

    try:
        # Get indices where condition is True
        matching_indices = series[condition_mask].index[:max_examples]

        for idx in matching_indices:
            value = series.loc[idx] if hasattr(idx, '__index__') else series.iloc[idx]
            examples.append({
                "row_number": int(idx),
                "value": str(value) if pd.notna(value) else "NULL",
            })
    except Exception:
        pass  # If collection fails, return empty examples

    return examples


def _add_examples_to_flags(flags: list, series: pd.Series, col_profile: dict) -> list:
    """
    Add example data to quality flags.

    Args:
        flags: List of flag dicts (without examples)
        series: The actual column data
        col_profile: The column profile dict

    Returns:
        Enhanced flags with examples and count added
    """
    enhanced_flags = []

    for flag in flags:
        flag_code = flag["code"]
        enhanced_flag = flag.copy()

        # Always add count from existing flag data or calculate
        if flag_code == "HIGH_MISSING":
            null_mask = series.isna()
            enhanced_flag["count"] = int(null_mask.sum())
            enhanced_flag["examples"] = _collect_examples(series, null_mask, max_examples=5)

        elif flag_code == "WHITESPACE_ISSUES":
            if series.dtype == 'object':
                str_series = series.astype(str)
                ws_mask = str_series.str.len() != str_series.str.strip().str.len()
                enhanced_flag["count"] = int(ws_mask.sum())
                enhanced_flag["examples"] = _collect_examples(series, ws_mask, max_examples=5)

        elif flag_code == "PLACEHOLDER_VALUES":
            if series.dtype == 'object':
                str_series = series.astype(str)
                lower_stripped = str_series.str.lower().str.strip()
                ph_mask = lower_stripped.isin(COMMON_PLACEHOLDERS)
                enhanced_flag["count"] = int(ph_mask.sum())
                enhanced_flag["examples"] = _collect_examples(series, ph_mask, max_examples=5)

        elif flag_code == "CONTAINS_NEGATIVES":
            try:
                neg_mask = series < 0
                enhanced_flag["count"] = int(neg_mask.sum())
                enhanced_flag["examples"] = _collect_examples(series, neg_mask, max_examples=5)
            except TypeError:
                pass

        elif flag_code == "CONTAINS_ZEROS":
            try:
                zero_mask = series == 0
                enhanced_flag["count"] = int(zero_mask.sum())
                enhanced_flag["examples"] = _collect_examples(series, zero_mask, max_examples=5)
            except TypeError:
                pass

        elif flag_code == "FUTURE_DATES":
            try:
                if pd.api.types.is_datetime64_any_dtype(series):
                    test_series = series
                elif series.dtype == 'object':
                    test_series = pd.to_datetime(series, errors='coerce')
                else:
                    test_series = series

                current_date = pd.Timestamp.now()
                future_mask = test_series > current_date
                enhanced_flag["count"] = int(future_mask.sum())
                enhanced_flag["examples"] = _collect_examples(test_series, future_mask, max_examples=5)
            except Exception:
                pass

        # Other flags: keep as-is (with count from col_profile if available)
        if "count" not in enhanced_flag:
            enhanced_flag["count"] = col_profile.get("null_count", 0)  # Default fallback

        if "examples" not in enhanced_flag:
            enhanced_flag["examples"] = []

        enhanced_flags.append(enhanced_flag)

    return enhanced_flags


def _analyze_duplicates(df: pd.DataFrame, max_duplicate_sets: int = 5, max_indices_per_set: int = 3) -> dict:
    """
    Analyze exact duplicate rows in the dataset.

    Args:
        df: The DataFrame to analyze
        max_duplicate_sets: Maximum number of duplicate sets to return
        max_indices_per_set: Maximum example row indices to store per set

    Returns:
        dict with duplicate analysis results
    """
    total_rows = len(df)

    if total_rows == 0:
        return {
            "total_rows": 0,
            "unique_rows": 0,
            "duplicate_rows": 0,
            "duplicate_pct": 0.0,
            "duplicate_sets": []
        }

    try:
        # Find unique rows
        unique_df = df.drop_duplicates()
        unique_rows = len(unique_df)
        duplicate_rows = total_rows - unique_rows
        duplicate_pct = (duplicate_rows / total_rows * 100) if total_rows > 0 else 0.0

        duplicate_sets = []

        if duplicate_rows > 0:
            # Find duplicate groups (rows that appear more than once)
            grouped = df.groupby(list(df.columns), dropna=False, sort=False)

            # Filter to only groups with more than 1 row
            duplicate_groups = grouped.filter(lambda x: len(x) > 1).groupby(list(df.columns), dropna=False)

            # Collect top duplicate sets
            for name, group in duplicate_groups:
                if len(duplicate_sets) >= max_duplicate_sets:
                    break

                count = len(group)
                if count > 1:
                    # Get first row as example
                    first_row = group.iloc[0].to_dict()

                    # Get example row indices
                    example_indices = group.index[:max_indices_per_set].tolist()

                    duplicate_sets.append({
                        "row_data": {
                            k: str(v) if pd.notna(v) else "NULL"
                            for k, v in first_row.items()
                        },
                        "count": count,
                        "example_indices": [int(idx) for idx in example_indices]
                    })

        return {
            "total_rows": total_rows,
            "unique_rows": unique_rows,
            "duplicate_rows": duplicate_rows,
            "duplicate_pct": round(duplicate_pct, 2),
            "duplicate_sets": duplicate_sets
        }

    except (TypeError, AttributeError) as e:
        # Handle unhashable types (lists, dicts in cells)
        return {
            "total_rows": total_rows,
            "unique_rows": -1,  # Indicates calculation failed
            "duplicate_rows": -1,
            "duplicate_pct": 0.0,
            "duplicate_sets": [],
            "error": "Unable to detect duplicates (unhashable column types present)"
        }
