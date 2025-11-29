# Data Profiler

A lightweight local Streamlit web app for comprehensive data quality profiling and reporting. Upload CSV or Excel files and receive instant data quality reports including type inference, missing data analysis, cardinality metrics, and automated quality flags.

![Data Profiler](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.51.0-red.svg)

## Features

### Core Functionality
- ✅ **File Upload**: Support for CSV and Excel (.xlsx, .xls) files
- ✅ **Dataset Overview**: Rows, columns, and memory usage statistics
- ✅ **Type Inference**: Automatic detection of numeric, datetime, boolean, categorical, and text columns
- ✅ **Comprehensive Statistics**:
  - Numeric columns: min, max, mean, median, std, percentiles
  - Datetime columns: min/max date ranges
  - All columns: missing %, unique count, top values with frequencies
- ✅ **Quality Flags**: Automatic detection of data quality issues
- ✅ **Export Options**: Download profiles as CSV or JSON

### Quality Flags

The profiler automatically detects and flags potential data quality issues:

| Flag | Severity | Description |
|------|----------|-------------|
| `HIGH_MISSING` | Warning | Configurable threshold (default 10%) of values are null |
| `CONSTANT_COLUMN` | Info | Column has only one unique value |
| `DOMINANT_VALUE` | Info | One value represents ≥95% of rows |
| `HIGH_CARDINALITY_CATEGORICAL` | Warning | Categorical/text column with >1000 unique values |
| `POTENTIAL_ID_COLUMN` | Info | High uniqueness (>90%) with ID-like column name |
| `MIXED_TYPES` | Warning | Object column contains multiple Python types |

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
├── profiling.py           # Core profiling engine with type inference
├── quality.py             # Data quality flag generation
├── io_utils.py            # File loading utilities
├── export_utils.py        # Export formatting (CSV/JSON)
├── requirements.txt       # Python dependencies
├── test_data/             # Sample datasets for testing
│   ├── sample_data.csv
│   ├── sample_products.xlsx
│   ├── quality_flags_test.csv
│   └── bi_dataset.csv
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

Sample test datasets are included in `test_data/`:

- `sample_data.csv`: Small dataset with mixed types and missing values
- `sample_products.xlsx`: Excel file with numeric data
- `quality_flags_test.csv`: Dataset designed to trigger all quality flags
- `bi_dataset.csv`: Realistic BI-style dataset (500 rows, 12 columns)

To test the profiler:
```bash
streamlit run app.py
```
Then upload any of the test files from the `test_data/` directory.

## Development

### Key Modules

- **profiling.py**: `profile_dataframe(df)` returns nested profile structure
- **quality.py**: `generate_quality_flags()` detects data quality issues
- **export_utils.py**: `profile_to_summary_df()` flattens profile for export

### Adding New Quality Flags

1. Define threshold constants in `quality.py`
2. Add detection logic in `generate_quality_flags()`
3. Return flag dict with `code`, `severity`, and `message`

### Extending Type Inference

Modify `_infer_type()` in `profiling.py` to add new type detection logic.

## Contributing

This is a weekend MVP project. Potential enhancements:

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
