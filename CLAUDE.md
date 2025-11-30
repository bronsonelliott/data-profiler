# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CSV/Excel Data Profiler** - A lightweight local Streamlit web app for comprehensive data quality profiling and reporting. Users upload CSV or Excel files and receive instant data quality/profile reports including type inference, missing data analysis, cardinality metrics, and automated quality flags.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install streamlit pandas openpyxl
```

### Running the Application
```bash
streamlit run app.py
```

### Updating Dependencies
```bash
# After adding new packages, update requirements
pip freeze > requirements.txt
```

## Architecture & Design

### Module Structure

The codebase follows a modular separation of concerns:

- **`app.py`** - Streamlit UI orchestration layer. Handles user interactions, file uploads, and coordinates between modules. Contains main layout logic (sidebar settings, dataset summary display, column summary table rendering).

- **`io_utils.py`** - File ingestion and loading logic. The `load_file(uploaded_file)` function handles CSV and XLSX format detection, error handling for corrupt files, and returns pandas DataFrames.

- **`profiling.py`** - Core profiling engine. Implements `profile_dataframe(df)` which returns a comprehensive profile dict with dataset-level stats and per-column metadata including type inference, missingness, cardinality, top values, and numeric/datetime statistics.

- **`quality.py`** - Data quality rule engine. The `generate_quality_flags(col_name, col_profile, total_rows)` function generates structured quality flags (code, severity, message) based on configurable thresholds for issues like high missingness, constant values, high cardinality, potential ID columns, and mixed types.

- **`export_utils.py`** - Export functionality. Contains `profile_to_summary_df(profile)` which flattens the nested profile dict into a tabular summary for CSV export.

### Profile Data Structure

The profiling engine returns a nested dict:

```python
{
  "dataset": {
    "n_rows": int,
    "n_columns": int,
    "memory_usage_bytes": int,
  },
  "columns": {
    column_name: {
      "pandas_dtype": str,
      "inferred_type": str,  # numeric, datetime, boolean, categorical, text, unknown
      "non_null_count": int,
      "null_count": int,
      "missing_pct": float,  # 0–100
      "unique_count": int,
      "top_values": [
        {"value": <repr>, "count": int, "pct": float},
        ...
      ],
      "numeric_stats": {...} or None,
      "datetime_stats": {...} or None,
      "quality_flags": [...]  # list of flag dicts
    },
    ...
  }
}
```

### Type Inference System

Maps pandas dtypes to simplified business types:
- **numeric**: `int*`, `float*` dtypes
- **datetime**: `datetime64[ns]` dtype
- **boolean**: `bool` dtype
- **categorical vs text**: For `object` dtype, use cardinality heuristic (low unique count → categorical, high unique count → text)
- **datetime inference**: For object columns, optionally sample values with `pd.to_datetime` to detect date strings

### Quality Flag Rules

Each flag includes `code`, `severity` (info/warning/error), and `message`:

**Basic Flags**:
- **HIGH_MISSING** (warning): missing_pct >= configurable threshold (default 10%)
- **CONSTANT_COLUMN** (info): unique_count == 1
- **DOMINANT_VALUE** (info): top value accounts for >= 95% of rows
- **HIGH_CARDINALITY_CATEGORICAL** (warning): categorical/text type with unique_count > 1000
- **POTENTIAL_ID_COLUMN** (info): unique_count / total_rows > 0.9 AND column name matches ID pattern (id, *_id, *id)
- **MIXED_TYPES** (warning): object dtype with multiple Python types detected

**Advanced Flags** (Phase 1-4 implementations):
- **SKEWED_DISTRIBUTION** (info): Numeric column has |skewness| > 2.0
- **CONTAINS_ZEROS** (info): Numeric column has > 10% zero values
- **CONTAINS_NEGATIVES** (warning): Amount/price columns with negative values detected
- **FUTURE_DATES** (warning): Datetime column contains dates beyond today
- **WHITESPACE_ISSUES** (warning): Text values with leading/trailing whitespace > 1%
- **PLACEHOLDER_VALUES** (info/warning): Common placeholders detected (N/A, null, unknown, etc.)
- **INCONSISTENT_CASING** (info): Text column has same values with different cases
- **SPECIAL_CHARACTERS** (info): Values contain non-printable special characters > 0.5%
- **DUPLICATE_ROWS** (info/warning): Exact duplicate rows detected (>1% info, >5% warning)

## Implementation Guidelines

### Type Inference
When implementing type inference, handle edge cases systematically:
- Test a sample of object columns for datetime parsing rather than entire column for performance
- Use `pd.to_datetime(errors="coerce")` to detect parsing failures
- Apply cardinality heuristic: `unique_count / total_rows < 0.05` suggests categorical

### Statistics Computation
For numeric columns, use pandas methods efficiently:
- Use `.describe()` for bulk stats computation
- Compute percentiles in single call: `df[col].quantile([0.25, 0.5, 0.75])`
- Handle null values appropriately (most stats methods skip nulls by default)

### Quality Flag Generation
Wire quality flags into profiling pipeline by calling `generate_quality_flags()` for each column after computing its stats, then attach results to `col_profile["quality_flags"]`.

### New Feature Implementations (Phase 1-4)

**Phase 1: Value Distribution Patterns**
- Compute skewness using `scipy.stats.skew()` for numeric columns
- Count zero and negative values as percentages of non-null values
- Detect future dates by comparing datetime values against `pd.Timestamp.now()`

**Phase 2: String Quality Checks**
- Use pandas `.str` vectorized methods for efficiency on large datasets
- Sample first 1000 rows for string analysis to maintain performance
- Detect whitespace with `.str.strip()` != original values
- Check for placeholder values against hardcoded list (N/A, null, None, unknown, etc.)
- Detect casing inconsistencies using `.str.lower()` comparisons
- Count non-printable characters using character code checks

**Phase 3: Sample Data Display**
- Collect 3-5 representative examples for each quality flag
- Include row numbers in examples for traceability
- Use `_collect_examples()` helper to extract flagged values
- Attach examples via `_add_examples_to_flags()` function

**Phase 4: Duplicate Detection**
- Use pandas `drop_duplicates()` for exact row duplication detection
- Perform duplicate analysis at dataset level (not per-column)
- Include duplicate count, percentage, and duplicate set details
- Severity: info for >1%, warning for >5%

### UI Layout Strategy
Streamlit layout follows this structure:
- **Sidebar**: File uploader + optional settings (missingness threshold, top N values count)
- **Main area**: Dataset summary → Column summary table → Optional per-column expanders
- Use `st.dataframe()` for displaying tabular data with built-in interactivity

### Export Implementation
For CSV export via `st.download_button`:
1. Call `profile_to_summary_df(profile)` to flatten nested profile
2. Convert DataFrame to CSV: `df.to_csv(index=False).encode('utf-8')`
3. Pass bytes to download button with appropriate MIME type

## Error Handling

Handle these failure modes gracefully:
- Empty files: Check `df.empty` and show informative message
- Columns with all nulls: Protect against division by zero in percentage calculations
- Mixed types: Catch exceptions during type inference and mark as "unknown"
- File format errors: Use try/except in `load_file()` and display clear error in Streamlit
- Large files: Consider streaming or chunking for files exceeding memory limits

## Testing Strategy

Test with representative datasets covering:
- Mostly numeric dataset (BI metrics, financial data)
- Mixed text/numeric dataset (customer records)
- Dataset with dates and significant missing values
- "Dirty" dataset with mixed types and high cardinality text columns

Validate that quality flags appear appropriately for each scenario.

## Testing

Comprehensive testing infrastructure is available in the `tests/` directory:

- **execute_all_tests.py**: Executes all 72 test cases (100% pass rate verified)
- **create_test_data.py**: Generates 5 test CSV files covering all features
- **run_tests.py**: Interactive testing with file upload simulation
- **test_automation.py**: Automated Playwright-based testing

Test documentation in `docs/`:
- **TEST_PLAN.md**: 72 comprehensive test cases organized in 6 categories
- **FINAL_TEST_REPORT.md**: Complete test results and sign-off
- **TESTING_GUIDE.md**: User-friendly testing guide with manual checklist

## Reference

Documentation files:
- **PRD.md**: Product requirements document with detailed specifications
- **README.md**: User guide with feature overview and usage instructions
- **docs/FEATURE_QUICK_REFERENCE.md**: Feature overview with quality flag thresholds
- **docs/IMPLEMENTATION_SUMMARY.md**: Technical implementation details
- **STATUS.md**: Project status and development progress
