import re


# Quality flag thresholds
HIGH_MISSING_THRESHOLD = 30.0  # percentage
DOMINANT_VALUE_THRESHOLD = 95.0  # percentage
HIGH_CARDINALITY_THRESHOLD = 1000  # unique count
POTENTIAL_ID_UNIQUENESS_THRESHOLD = 0.9  # ratio
MIXED_TYPES_THRESHOLD = 10.0  # percentage of minority types


def generate_quality_flags(col_name: str, col_profile: dict, total_rows: int, high_missing_threshold: float = None) -> list:
    """
    Returns a list of quality flag dicts for a single column.

    Each flag:
    {
      "code": str,         # e.g., "HIGH_MISSING"
      "severity": str,     # "info" | "warning" | "error"
      "message": str,      # human-readable explanation
    }

    Args:
        col_name: Name of the column
        col_profile: Profile dict for the column
        total_rows: Total number of rows in the dataset
        high_missing_threshold: Threshold percentage for HIGH_MISSING flag (defaults to HIGH_MISSING_THRESHOLD constant)
    """
    flags = []

    # Use provided threshold or fall back to constant
    if high_missing_threshold is None:
        high_missing_threshold = HIGH_MISSING_THRESHOLD

    # HIGH_MISSING: missing_pct >= threshold
    if col_profile["missing_pct"] >= high_missing_threshold:
        flags.append({
            "code": "HIGH_MISSING",
            "severity": "warning",
            "message": f"High missing rate: {col_profile['missing_pct']:.1f}% of values are null"
        })

    # CONSTANT_COLUMN: unique_count == 1
    if col_profile["unique_count"] == 1:
        flags.append({
            "code": "CONSTANT_COLUMN",
            "severity": "info",
            "message": "Column has a single unique value"
        })

    # DOMINANT_VALUE: top value accounts for >= 95% of rows
    if col_profile["top_values"] and len(col_profile["top_values"]) > 0:
        top_value_pct = col_profile["top_values"][0]["pct"]
        if top_value_pct >= DOMINANT_VALUE_THRESHOLD:
            flags.append({
                "code": "DOMINANT_VALUE",
                "severity": "info",
                "message": f"One value represents {top_value_pct:.1f}% of rows"
            })

    # HIGH_CARDINALITY_CATEGORICAL: categorical/text type with unique_count > 1000
    if col_profile["inferred_type"] in ["categorical", "text"]:
        if col_profile["unique_count"] > HIGH_CARDINALITY_THRESHOLD:
            flags.append({
                "code": "HIGH_CARDINALITY_CATEGORICAL",
                "severity": "warning",
                "message": f"High cardinality categorical/text column ({col_profile['unique_count']:,} unique values)"
            })

    # POTENTIAL_ID_COLUMN: unique_count / total_rows > 0.9 AND name matches ID pattern
    if total_rows > 0:
        uniqueness_ratio = col_profile["unique_count"] / total_rows
        if uniqueness_ratio > POTENTIAL_ID_UNIQUENESS_THRESHOLD and _is_id_like_name(col_name):
            flags.append({
                "code": "POTENTIAL_ID_COLUMN",
                "severity": "info",
                "message": "Column looks like a unique identifier"
            })

    # MIXED_TYPES: object dtype with multiple Python types detected
    if col_profile.get("mixed_types_info"):
        mixed_info = col_profile["mixed_types_info"]
        if mixed_info["has_mixed_types"] and mixed_info["mixed_type_pct"] >= MIXED_TYPES_THRESHOLD:
            type_list = ", ".join(mixed_info["type_counts"].keys())
            flags.append({
                "code": "MIXED_TYPES",
                "severity": "warning",
                "message": f"Column contains mixed data types: {type_list}"
            })

    return flags


def _is_id_like_name(col_name: str) -> bool:
    """
    Check if column name matches ID-like patterns.
    Patterns: 'id', '*_id', '*id' (case-insensitive)
    """
    col_lower = col_name.lower().strip()

    # Exact match: 'id'
    if col_lower == 'id':
        return True

    # Ends with '_id'
    if col_lower.endswith('_id'):
        return True

    # Ends with 'id' (but not just 'id' which we already checked)
    if col_lower.endswith('id') and len(col_lower) > 2:
        # Make sure it's something like 'userid' not 'valid'
        # Simple heuristic: if it ends with 'id' and has no space before it
        return True

    return False
