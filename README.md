# Data Profiler

A lightweight local Streamlit web app for comprehensive data quality profiling and reporting. Upload CSV or Excel files and receive instant data quality reports including type inference, missing data analysis, cardinality metrics, and automated quality flags.

![Data Profiler](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.51.0-red.svg)

## Features

### Core Functionality
- ✅ **File Upload**: Support for CSV and Excel (.xlsx, .xls) files
- ✅ **Dataset Overview**: Rows, columns, memory usage, and duplicate analysis
- ✅ **Type Inference**: Automatic detection of numeric, datetime, boolean, categorical, and text columns
- ✅ **Comprehensive Statistics**:
  - Numeric columns: min, max, mean, median, std, percentiles, skewness, zero/negative counts
  - Datetime columns: min/max date ranges, future date detection
  - All columns: missing %, unique count, top values with frequencies
- ✅ **Data Quality Analysis**:
  - 6 basic quality flags for common issues
  - 9 advanced quality flags for distribution patterns, string quality, and duplicates
  - Sample values with row numbers for each flagged condition
- ✅ **Export Options**: Download column summary (CSV), dataset summary (CSV), or full profile (JSON)

### Quality Flags

The profiler automatically detects and flags potential data quality issues:

**Basic Flags**:
| Flag | Severity | Description |
|------|----------|-------------|
| `HIGH_MISSING` | Warning | Configurable threshold (default 10%) of values are null |
| `CONSTANT_COLUMN` | Info | Column has only one unique value |
| `DOMINANT_VALUE` | Info | One value represents ≥95% of rows |
| `HIGH_CARDINALITY_CATEGORICAL` | Warning | Categorical/text column with >1000 unique values |
| `POTENTIAL_ID_COLUMN` | Info | High uniqueness (>90%) with ID-like column name |
| `MIXED_TYPES` | Warning | Object column contains multiple Python types |

**Advanced Flags** (NEW):
| Flag | Severity | Description |
|------|----------|-------------|
| `SKEWED_DISTRIBUTION` | Info | Numeric column has highly skewed distribution (\|skewness\| > 2.0) |
| `CONTAINS_ZEROS` | Info | Numeric column has >10% zero values |
| `CONTAINS_NEGATIVES` | Warning | Amount/price columns with negative values |
| `FUTURE_DATES` | Warning | Datetime column contains dates in the future |
| `WHITESPACE_ISSUES` | Warning | Text values with leading/trailing whitespace (>1%) |
| `PLACEHOLDER_VALUES` | Info/Warning | Common placeholders detected (N/A, null, unknown, etc.) |
| `INCONSISTENT_CASING` | Info | Text column has same values with different cases |
| `SPECIAL_CHARACTERS` | Info | Values contain non-printable special characters (>0.5%) |
| `DUPLICATE_ROWS` | Info/Warning | Exact duplicate rows detected (>1% is info, >5% is warning) |

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download this repository**
   ```bash
   cd data-profiler
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the App

```bash
streamlit run app.py
```

The app will automatically open in your default web browser at `http://localhost:8501`

### Basic Workflow

1. **Upload a File**: Use the sidebar to upload a CSV or Excel file (up to ~50MB)

2. **View Dataset Summary**: See high-level statistics about your dataset
   - Number of rows and columns
   - Memory usage
   - Quick overview

3. **Review Column Profiles**: Examine the comprehensive column summary table
   - Inferred data types
   - Missing value percentages
   - Unique counts
   - Top values
   - Quality flags

4. **Explore Details** (Optional): Enable "Show detailed column stats" in the sidebar for:
   - Per-column expandable sections
   - Full numeric/datetime statistics
   - Color-coded quality flags
   - Complete top values tables

5. **Export Results**: Download your profile as:
   - **CSV**: Tabular format for easy sharing and Excel analysis
   - **JSON**: Complete structured data for programmatic use

### Settings

Access customization options in the sidebar:

- **Null value threshold (%)**: Set the threshold for flagging columns with excessive null values (0-100%, default 10%). Columns meeting or exceeding this threshold are highlighted in yellow in the summary table and flagged in detailed views.
- **Top N values to display**: Choose how many frequent values to show (3-10)
- **Show detailed column stats**: Toggle per-column expandable detail views

## Project Structure

```
data-profiler/
├── app.py                 # Streamlit UI application
├── profiling.py           # Core profiling engine with type inference and 4 new features
├── quality.py             # Data quality flag generation (9 new flags)
├── io_utils.py            # File loading utilities
├── export_utils.py        # Export formatting (CSV/JSON) with new feature exports
├── requirements.txt       # Python dependencies
│
├── docs/                  # Documentation
│   ├── TEST_PLAN.md            # Comprehensive 72-test plan for all features
│   ├── FINAL_TEST_REPORT.md    # All 72 tests executed - 100% pass rate
│   ├── TESTING_GUIDE.md        # User-friendly testing guide
│   ├── FEATURE_QUICK_REFERENCE.md # Feature overview and usage tips
│   └── IMPLEMENTATION_SUMMARY.md  # Technical implementation details
│
├── tests/                 # Test scripts and automation
│   ├── execute_all_tests.py    # Executes all 72 tests (100% pass rate)
│   ├── create_test_data.py     # Generates 5 comprehensive test CSV files
│   ├── run_tests.py            # Interactive runtime testing
│   └── test_automation.py      # Automated Playwright-based testing
│
├── test_data/             # Auto-generated test datasets
│   ├── test_numeric.csv        # 100 rows: skewness, zeros, negatives
│   ├── test_strings.csv        # 100 rows: whitespace, placeholders, casing, special chars
│   ├── test_dates.csv          # 100 rows: historical and future dates
│   ├── test_duplicates.csv     # 200 rows: 40% exact duplicates
│   ├── test_all_features.csv   # 1050 rows: all features integrated
│   ├── sample_data.csv         # Original sample data
│   ├── sample_products.xlsx    # Original sample Excel file
│   ├── quality_flags_test.csv  # Original quality flags test file
│   └── bi_dataset.csv          # Original BI-style sample dataset
│
├── README.md              # This file
├── PRD.md                 # Product requirements document
├── CLAUDE.md              # Development guidance
└── STATUS.md              # Project status and progress
```

## Technical Details

### Type Inference System

The profiler uses a multi-stage approach to infer column types:

1. **Direct dtype mapping**: Numeric, datetime, boolean types detected from pandas dtypes
2. **Datetime detection**: Object columns tested with `pd.to_datetime()` for date strings
3. **Cardinality heuristic**: Low uniqueness ratio (<5%) → categorical, high → text

### Performance

- Target: Profile datasets up to ~50MB or ~1-2M rows in under 10 seconds
- Memory profiling uses `deep=True` for accuracy (may be slower on very large files)
- Mixed type detection samples up to 100 values per column for efficiency

### Limitations

- Maximum file size: ~50MB (configurable, limited by available memory)
- Excel support: First sheet only
- Datetime parsing: Uses pandas datetime inference (may produce warnings)

## Example Use Cases

1. **Initial Data Exploration**: Quickly understand a new dataset before analysis
2. **Data Quality Assessment**: Identify issues before loading into BI tools or databases
3. **Documentation**: Generate shareable reports for stakeholders or data teams
4. **ETL Validation**: Verify data structure and quality after transformations

## Testing

### Automated Testing

Comprehensive testing infrastructure with 72 test cases (100% pass rate):

**Run all tests:**
```bash
python tests/execute_all_tests.py
```

**Test scripts in `tests/` directory:**
- `execute_all_tests.py` - Executes all 72 test cases with detailed reporting
- `create_test_data.py` - Generates 5 comprehensive test CSV files
- `run_tests.py` - Interactive testing with file upload simulation
- `test_automation.py` - Automated Playwright-based testing

**Test documentation in `docs/` directory:**
- `TEST_PLAN.md` - 72 comprehensive test cases (Unit, Runtime, Functionality, UI, Export, Edge Cases)
- `FINAL_TEST_REPORT.md` - Complete test results and sign-off
- `TESTING_GUIDE.md` - User-friendly testing guide with manual checklist

### Manual Testing

Sample test datasets are included in `test_data/`:

- `test_numeric.csv` - 100 rows testing skewness, zeros, negatives
- `test_strings.csv` - 100 rows testing whitespace, placeholders, casing, special chars
- `test_dates.csv` - 100 rows testing historical and future dates
- `test_duplicates.csv` - 200 rows with 40% exact duplicates
- `test_all_features.csv` - 1050 rows with all features integrated
- `sample_data.csv` - Original sample data with mixed types and missing values
- `sample_products.xlsx` - Excel file with numeric data
- `quality_flags_test.csv` - Dataset designed to trigger quality flags
- `bi_dataset.csv` - Realistic BI-style dataset (500 rows, 12 columns)

To manually test the profiler:
```bash
streamlit run app.py
```
Then upload any test file from the `test_data/` directory.

## Development

### Key Modules

- **profiling.py**: `profile_dataframe(df)` returns nested profile structure
- **quality.py**: `generate_quality_flags()` detects data quality issues
- **export_utils.py**: `profile_to_summary_df()` flattens profile for export

### New Features Implementation (Phase 1-4)

**Phase 1: Value Distribution Patterns** - profiling.py
- `_compute_numeric_stats()`: Added skewness, zero_count, zero_pct, negative_count, negative_pct
- `_compute_datetime_stats()`: Added future_count, future_pct, max_future_date
- Quality flags: SKEWED_DISTRIBUTION, CONTAINS_ZEROS, CONTAINS_NEGATIVES, FUTURE_DATES

**Phase 2: String Quality Checks** - profiling.py
- `_analyze_string_quality()`: Comprehensive string analysis (185 lines)
- Analyzes whitespace, placeholders, casing, special characters
- Quality flags: WHITESPACE_ISSUES, PLACEHOLDER_VALUES, INCONSISTENT_CASING, SPECIAL_CHARACTERS

**Phase 3: Sample Data Display** - profiling.py
- `_collect_examples()`: Extracts 3-5 sample values for flagged conditions
- `_add_examples_to_flags()`: Enriches quality flags with examples and row numbers

**Phase 4: Duplicate Detection** - profiling.py
- `_analyze_duplicates()`: Dataset-level exact duplicate detection
- Returns duplicate count, percentage, and duplicate set details
- Quality flag: DUPLICATE_ROWS (info >1%, warning >5%)

### Adding New Quality Flags

1. Define threshold constants in `quality.py` (e.g., SKEWNESS_THRESHOLD = 2.0)
2. Add detection logic in `generate_quality_flags()` for column-level or `generate_dataset_quality_flags()` for dataset-level
3. Return flag dict with `code`, `severity`, and `message`
4. Optionally add to `_add_examples_to_flags()` to include sample values

### Extending Type Inference

Modify `_infer_type()` in `profiling.py` to add new type detection logic.

## Project Status

### Completed Features ✅
- [x] Core data profiling and type inference
- [x] Basic quality flags (6 flags)
- [x] Advanced quality flags - Phase 1: Value Distribution Patterns (4 flags)
- [x] Advanced quality flags - Phase 2: String Quality Checks (4 flags)
- [x] Advanced quality flags - Phase 3: Sample Data Display with row numbers
- [x] Advanced quality flags - Phase 4: Duplicate Detection
- [x] CSV/JSON export functionality
- [x] Comprehensive testing (72 test cases, 100% pass rate)
- [x] Full test automation infrastructure

### Potential Future Enhancements
- [ ] Histogram visualizations for numeric columns
- [ ] Correlation analysis
- [ ] Data sampling for very large files
- [ ] Multiple sheet support for Excel files
- [ ] Configurable quality flag thresholds
- [ ] Integration with ydata-profiling for advanced analysis

## License

MIT License - feel free to use and modify as needed.

## Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Web app framework
- [pandas](https://pandas.pydata.org/) - Data analysis and manipulation
- [openpyxl](https://openpyxl.readthedocs.io/) - Excel file support
