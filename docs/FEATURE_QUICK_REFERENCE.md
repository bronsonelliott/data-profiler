# Data Profiler - New Features Quick Reference

## 🎯 Quick Start

Run the application:
```bash
streamlit run app.py
```

## 📊 New Quality Flags & Thresholds

### Phase 1: Distribution Patterns

| Flag | Threshold | Severity | Meaning |
|------|-----------|----------|---------|
| `SKEWED_DISTRIBUTION` | \|skewness\| > 2.0 | info | Numeric column has extreme skew |
| `CONTAINS_ZEROS` | >10% zeros | info | Numeric column has many zeros |
| `CONTAINS_NEGATIVES` | Any negative | warning | Negative values in amount/price columns |
| `FUTURE_DATES` | Any future date | warning | Datetime column has dates in future |

### Phase 2: String Quality

| Flag | Threshold | Severity | Meaning |
|------|-----------|----------|---------|
| `WHITESPACE_ISSUES` | >1% whitespace | warning | Leading/trailing spaces detected |
| `PLACEHOLDER_VALUES` | Any placeholders | info/warning | Common placeholder values found |
| `INCONSISTENT_CASING` | Case variants | info | Same value with different cases |
| `SPECIAL_CHARACTERS` | >0.5% special | info | Non-printable characters found |

### Phase 4: Dataset Level

| Flag | Threshold | Severity | Meaning |
|------|-----------|----------|---------|
| `DUPLICATE_ROWS` | 1-5% duplicates | info | Some duplicate rows detected |
| `DUPLICATE_ROWS` | >5% duplicates | warning | Many duplicate rows detected |

## 🔍 What Each Feature Does

### Distribution Pattern Analysis
- **Skewness**: Detects asymmetric distributions (useful for ML features)
- **Zeros**: Flags columns with unusual number of zero values
- **Negatives**: Catches impossible negative values in amount columns
- **Future Dates**: Identifies data quality issues with dates

### String Quality Analysis
- **Whitespace**: Finds values with leading/trailing spaces (data cleaning issue)
- **Placeholders**: Identifies N/A, null, unknown, etc. (helps with missing data handling)
- **Casing**: Detects "Active", "active", "ACTIVE" (standardization issue)
- **Special Characters**: Finds unusual characters that may corrupt data

### Sample Data Display
- Every flag shows 3-5 real examples from your data
- Row numbers included for easy navigation
- Click "View Examples" to expand and see the actual values

### Duplicate Detection
- Shows exact duplicate rows in your dataset
- Displays duplicate sets with row counts
- Provides example row indices for verification
- Separate dataset summary CSV export

## 📈 Enhanced Metrics in Profile

### Column-Level (in detailed view):

**Numeric Columns:**
- Skewness value
- Zero count and percentage
- Negative count and percentage (if present)

**Datetime Columns:**
- Future date count and percentage
- Latest future date (if present)

**Text/Categorical Columns:**
- Whitespace count and percentage
- Placeholder count and percentage
- Casing inconsistency groups
- Special character count and percentage

### Dataset-Level (in dataset summary):

- Total rows
- Unique rows
- Duplicate rows
- Duplicate percentage

## 💾 Export Options

1. **Column Summary CSV**
   - All column-level metrics and flags
   - Includes new distribution and string quality metrics

2. **Dataset Summary CSV**
   - Dataset-level metrics
   - Duplicate analysis results
   - Quick dataset overview

3. **Full Profile JSON**
   - Complete profile structure
   - All metrics and examples
   - Programmatic access to all data

## 🎨 UI Improvements

### Numeric Stats Display
- Extended to show 4 columns instead of 3
- Added Skewness metric
- Conditional display of Zeros/Negatives

### String Quality Section
- New subsection in detailed column view
- 2-column layout for clean display
- Shows all 4 string quality metrics at a glance

### Duplicate Analysis Section
- New subsection in dataset summary
- 3 metrics: Unique Rows, Duplicate Rows, Duplicate %
- Expandable "View Duplicate Sets" for details

### Quality Flags Display
- Each flag can be expanded to view examples
- Shows row numbers and actual values
- Helps analysts understand issues quickly

## 🔧 Configuration Constants

All thresholds are configurable in `quality.py`:

```python
# Distribution thresholds
SKEWNESS_THRESHOLD = 2.0
ZERO_PCT_THRESHOLD = 10.0

# String quality thresholds
WHITESPACE_THRESHOLD = 1.0
PLACEHOLDER_WARNING_THRESHOLD = 10.0
SPECIAL_CHAR_THRESHOLD = 0.5

# Duplicate thresholds
DUPLICATE_WARNING_THRESHOLD = 5.0
```

Adjust these values based on your data quality standards.

## 📋 Common Use Cases

### Case 1: Cleaning Raw Data
1. Upload CSV
2. Check String Quality flags (whitespace, placeholders)
3. View examples to see exact issues
4. Use row numbers to locate and fix issues

### Case 2: Financial Data Validation
1. Upload CSV
2. Check Distribution flags (negatives in amounts)
3. Check for future dates in transaction columns
4. Export dataset summary for compliance review

### Case 3: Deduplication Project
1. Upload CSV
2. Check Duplicate Analysis section
3. View duplicate sets to understand patterns
4. Export dataset summary with duplicate metrics

### Case 4: Data Quality Report
1. Upload CSV
2. Review all flags and quality metrics
3. View examples for each issue
4. Export all three CSV files for stakeholders

## 🚀 Tips & Best Practices

1. **Review Examples First**: Always look at the examples to understand what a flag means
2. **Check Dataset Summary**: Always start with the overall duplicate and metric overview
3. **Use Row Numbers**: The row numbers in examples help you locate issues in source data
4. **Export for Sharing**: Use CSV exports for non-technical stakeholders
5. **Threshold Tuning**: Adjust thresholds in `quality.py` based on your data domain

## 📞 Need More Info?

See `IMPLEMENTATION_SUMMARY.md` for detailed technical documentation
See `data-profiler-feature-spec.md` for original feature specifications
