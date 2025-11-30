import pandas as pd


def profile_to_summary_df(profile: dict) -> pd.DataFrame:
    """
    Flatten column profiles into a single DataFrame with one row per column.

    Converts the nested profile structure into a tabular format suitable
    for display and CSV export.
    """
    rows = []

    for col_name, col_profile in profile["columns"].items():
        # Format top values as comma-separated string
        top_values_str = _format_top_values(col_profile["top_values"])

        # Format quality flags as semicolon-separated string
        flags_str = _format_quality_flags(col_profile["quality_flags"])

        # Format numeric stats if available
        numeric_stats_str = _format_numeric_stats(col_profile.get("numeric_stats"))

        # Format datetime stats if available
        datetime_stats_str = _format_datetime_stats(col_profile.get("datetime_stats"))

        # Format string quality if available
        string_quality_str = _format_string_quality(col_profile.get("string_quality"))

        row = {
            "Column": col_name,
            "Type": col_profile["inferred_type"],
            "Pandas Dtype": col_profile["pandas_dtype"],
            "Missing %": col_profile["missing_pct"],
            "Null Count": col_profile["null_count"],
            "Non-Null Count": col_profile["non_null_count"],
            "Unique Count": col_profile["unique_count"],
            "Top Values": top_values_str,
            "Numeric Stats": numeric_stats_str,
            "Datetime Range": datetime_stats_str,
            "String Quality": string_quality_str,
            "Quality Flags": flags_str,
        }

        rows.append(row)

    return pd.DataFrame(rows)


def _format_top_values(top_values: list, max_display: int = 3) -> str:
    """
    Format top values as a readable string.
    Example: "value1 (45%), value2 (30%), value3 (12%)"
    """
    if not top_values:
        return ""

    formatted = []
    for item in top_values[:max_display]:
        value = item["value"]
        pct = item["pct"]
        # Truncate long values
        if len(str(value)) > 20:
            value = str(value)[:17] + "..."
        formatted.append(f"{value} ({pct:.1f}%)")

    result = ", ".join(formatted)

    # Indicate if there are more values
    if len(top_values) > max_display:
        result += "..."

    return result


def _format_quality_flags(flags: list) -> str:
    """
    Format quality flags as a readable string.
    Example: "High missing; Potential ID"
    """
    if not flags:
        return ""

    # Extract just the short message or code
    flag_messages = []
    for flag in flags:
        # Use a shortened version of the message
        code = flag["code"]
        readable = code.replace("_", " ").title()
        flag_messages.append(readable)

    return "; ".join(flag_messages)


def _format_numeric_stats(stats: dict) -> str:
    """
    Format numeric statistics as a readable string.
    Example: "min: 0.5, max: 100.2, mean: 45.3, skew: 1.5, zeros: 5.0%"
    """
    if not stats:
        return ""

    parts = []
    if stats.get("min") is not None:
        parts.append(f"min: {stats['min']:.2f}")
    if stats.get("max") is not None:
        parts.append(f"max: {stats['max']:.2f}")
    if stats.get("mean") is not None:
        parts.append(f"mean: {stats['mean']:.2f}")
    if stats.get("skewness") is not None:
        parts.append(f"skew: {stats['skewness']:.2f}")
    if stats.get("zero_pct") is not None and stats['zero_pct'] > 0:
        parts.append(f"zeros: {stats['zero_pct']:.1f}%")
    if stats.get("negative_pct") is not None and stats['negative_pct'] > 0:
        parts.append(f"negatives: {stats['negative_pct']:.1f}%")

    return ", ".join(parts) if parts else ""


def _format_datetime_stats(stats: dict) -> str:
    """
    Format datetime statistics as a readable string.
    Example: "2020-01-01 to 2023-12-31; ⚠️ 5 future dates"
    """
    if not stats:
        return ""

    min_date = stats.get("min")
    max_date = stats.get("max")

    parts = []
    if min_date and max_date:
        # Extract just the date part if it's a full ISO datetime
        min_str = min_date.split("T")[0] if "T" in min_date else min_date
        max_str = max_date.split("T")[0] if "T" in max_date else max_date
        parts.append(f"{min_str} to {max_str}")
    elif min_date:
        parts.append(f"from {min_date.split('T')[0]}")
    elif max_date:
        parts.append(f"to {max_date.split('T')[0]}")

    # Add future dates warning if present
    if stats.get("future_count", 0) > 0:
        parts.append(f"⚠️ {stats['future_count']} future dates")

    return "; ".join(parts) if parts else ""


def _format_string_quality(sq: dict) -> str:
    """
    Format string quality stats as a readable string.
    Example: "whitespace: 1.5%; placeholders: 5%; casing issues; special chars: 0.8%"
    """
    if not sq:
        return ""

    parts = []
    if sq.get("whitespace_pct", 0) > 0:
        parts.append(f"whitespace: {sq['whitespace_pct']:.1f}%")
    if sq.get("placeholder_pct", 0) > 0:
        parts.append(f"placeholders: {sq['placeholder_pct']:.1f}%")
    if sq.get("casing_issues"):
        parts.append("casing issues")
    if sq.get("special_char_pct", 0) > 0:
        parts.append(f"special chars: {sq['special_char_pct']:.1f}%")

    return "; ".join(parts) if parts else ""


def dataset_summary_to_dict(profile: dict) -> dict:
    """
    Extract dataset-level summary for export.

    Returns:
        dict suitable for CSV export
    """
    dataset = profile.get("dataset", {})
    dup_analysis = dataset.get("duplicate_analysis", {})

    summary = {
        "Total Rows": dataset.get("n_rows", 0),
        "Total Columns": dataset.get("n_columns", 0),
        "Memory Usage (MB)": round(dataset.get("memory_usage_bytes", 0) / (1024 * 1024), 2),
        "Unique Rows": dup_analysis.get("unique_rows", 0),
        "Duplicate Rows": dup_analysis.get("duplicate_rows", 0),
        "Duplicate %": dup_analysis.get("duplicate_pct", 0),
    }

    return summary
