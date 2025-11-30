import re


# Quality flag thresholds
HIGH_MISSING_THRESHOLD = 30.0  # percentage
DOMINANT_VALUE_THRESHOLD = 95.0  # percentage
HIGH_CARDINALITY_THRESHOLD = 1000  # unique count
POTENTIAL_ID_UNIQUENESS_THRESHOLD = 0.9  # ratio
MIXED_TYPES_THRESHOLD = 10.0  # percentage of minority types

# Distribution pattern thresholds
SKEWNESS_THRESHOLD = 2.0  # |skewness| > 2.0 is highly skewed
ZERO_PCT_THRESHOLD = 10.0  # Flag if >10% zeros
NEGATIVE_COL_PATTERNS = [  # Columns where negatives are unusual
    'amount', 'price', 'cost', 'quantity', 'count', 'total'
]

# String quality thresholds
WHITESPACE_THRESHOLD = 1.0  # percentage
PLACEHOLDER_INFO_THRESHOLD = 1.0  # percentage (info severity)
PLACEHOLDER_WARNING_THRESHOLD = 10.0  # percentage (warning severity)
SPECIAL_CHAR_THRESHOLD = 0.5  # percentage

# Duplicate detection thresholds
DUPLICATE_INFO_THRESHOLD = 1.0  # percentage
DUPLICATE_WARNING_THRESHOLD = 5.0  # percentage


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

    # SKEWED_DISTRIBUTION: |skewness| > 2.0
    numeric_stats = col_profile.get("numeric_stats")
    if numeric_stats and numeric_stats.get("skewness") is not None:
        skew_val = numeric_stats["skewness"]
        if abs(skew_val) > SKEWNESS_THRESHOLD:
            flags.append({
                "code": "SKEWED_DISTRIBUTION",
                "severity": "info",
                "message": f"Highly skewed distribution (skewness: {skew_val:.2f})"
            })

    # CONTAINS_ZEROS: >10% zeros
    if numeric_stats and numeric_stats.get("zero_pct", 0) > ZERO_PCT_THRESHOLD:
        flags.append({
            "code": "CONTAINS_ZEROS",
            "severity": "info",
            "message": f"Contains {numeric_stats['zero_count']:,} zeros ({numeric_stats['zero_pct']:.1f}%)"
        })

    # CONTAINS_NEGATIVES: For amount/price/count columns
    if numeric_stats and numeric_stats.get("negative_count", 0) > 0:
        col_lower = col_name.lower()
        if any(pattern in col_lower for pattern in NEGATIVE_COL_PATTERNS):
            flags.append({
                "code": "CONTAINS_NEGATIVES",
                "severity": "warning",
                "message": f"Contains {numeric_stats['negative_count']:,} negative values ({numeric_stats['negative_pct']:.1f}%)"
            })

    # FUTURE_DATES: Any future dates
    datetime_stats = col_profile.get("datetime_stats")
    if datetime_stats and datetime_stats.get("future_count", 0) > 0:
        flags.append({
            "code": "FUTURE_DATES",
            "severity": "warning",
            "message": f"Contains {datetime_stats['future_count']:,} future dates ({datetime_stats['future_pct']:.1f}%)"
        })

    # String quality flags
    string_quality = col_profile.get("string_quality")
    if string_quality:
        # WHITESPACE_ISSUES: >1% with whitespace
        if string_quality.get("whitespace_pct", 0) > WHITESPACE_THRESHOLD:
            flags.append({
                "code": "WHITESPACE_ISSUES",
                "severity": "warning",
                "message": f"Contains {string_quality['whitespace_count']:,} values with leading/trailing whitespace ({string_quality['whitespace_pct']:.1f}%)"
            })

        # PLACEHOLDER_VALUES: Present
        placeholder_pct = string_quality.get("placeholder_pct", 0)
        if placeholder_pct > 0:
            severity = "warning" if placeholder_pct >= PLACEHOLDER_WARNING_THRESHOLD else "info"
            placeholder_list = ", ".join(string_quality.get("placeholder_values", [])[:3])
            flags.append({
                "code": "PLACEHOLDER_VALUES",
                "severity": severity,
                "message": f"Contains {string_quality['placeholder_count']:,} placeholder values ({placeholder_pct:.1f}%): {placeholder_list}"
            })

        # INCONSISTENT_CASING: Detected
        if string_quality.get("casing_issues", False):
            flags.append({
                "code": "INCONSISTENT_CASING",
                "severity": "info",
                "message": f"Inconsistent casing detected ({string_quality['casing_groups']} groups with case variants)"
            })

        # SPECIAL_CHARACTERS: >0.5%
        if string_quality.get("special_char_pct", 0) > SPECIAL_CHAR_THRESHOLD:
            flags.append({
                "code": "SPECIAL_CHARACTERS",
                "severity": "info",
                "message": f"Contains {string_quality['special_char_count']:,} values with special/non-printable characters ({string_quality['special_char_pct']:.1f}%)"
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


def generate_dataset_quality_flags(dataset_profile: dict) -> list:
    """
    Generate quality flags for the entire dataset.

    Args:
        dataset_profile: The 'dataset' section of the profile dict

    Returns:
        List of dataset-level quality flag dicts
    """
    flags = []

    # DUPLICATE_ROWS: Flag if duplicates detected
    dup_analysis = dataset_profile.get("duplicate_analysis", {})
    dup_pct = dup_analysis.get("duplicate_pct", 0)

    if dup_pct > 0:
        severity = "warning" if dup_pct >= DUPLICATE_WARNING_THRESHOLD else "info"
        dup_count = dup_analysis.get("duplicate_rows", 0)

        flags.append({
            "code": "DUPLICATE_ROWS",
            "severity": severity,
            "message": f"Dataset contains {dup_count:,} duplicate rows ({dup_pct:.1f}%)",
            "count": dup_count,
        })

    return flags
