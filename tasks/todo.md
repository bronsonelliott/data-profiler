# Saturday Work Plan - Data Profiler

## Goal
Implement the core profiling engine, quality flags, export utilities, and integrate everything into the UI.

## Todo Items

### Phase 1: Core Profiling Engine
- [ ] Implement `profile_dataframe(df)` in `profiling.py`
  - [ ] Create dataset-level stats (rows, columns, memory)
  - [ ] Implement type inference logic (numeric, datetime, boolean, categorical, text, unknown)
  - [ ] Calculate per-column basic stats (null count, missing %, unique count)
  - [ ] Compute top N values with frequencies
  - [ ] Add numeric statistics (min, max, mean, median, std, percentiles)
  - [ ] Add datetime statistics (min, max dates)

### Phase 2: Quality Flags Module
- [ ] Create `quality.py` module
- [ ] Implement `generate_quality_flags(col_name, col_profile, total_rows)` function
- [ ] Add quality flag rules:
  - [ ] HIGH_MISSING (≥30% missing)
  - [ ] CONSTANT_COLUMN (single unique value)
  - [ ] DOMINANT_VALUE (≥95% one value)
  - [ ] HIGH_CARDINALITY_CATEGORICAL (>1000 unique for text/categorical)
  - [ ] POTENTIAL_ID_COLUMN (>90% unique + ID-like name)

### Phase 3: Export Utilities
- [ ] Create `export_utils.py` module
- [ ] Implement `profile_to_summary_df(profile)` to flatten nested profile structure

### Phase 4: UI Integration
- [ ] Update `app.py` to integrate profiling
- [ ] Add dataset summary display (rows, columns, memory)
- [ ] Display column summary table with profile data
- [ ] Add loading spinner for profiling operation

### Phase 5: Testing
- [ ] Test with sample_data.csv (mixed types, missing values)
- [ ] Test with sample_products.xlsx (numeric stats, Excel format)
- [ ] Verify quality flags trigger correctly
- [ ] Validate type inference accuracy

## Implementation Notes

### Type Inference Strategy
- numeric: int*, float* dtypes
- datetime: datetime64[ns] dtype
- boolean: bool dtype
- categorical vs text: Use 5% uniqueness ratio (unique_count / total_rows < 0.05 → categorical)
- For object columns with date strings: optionally test with pd.to_datetime

### Quality Flag Structure
Each flag should be a dict with:
```python
{
  "code": str,         # e.g., "HIGH_MISSING"
  "severity": str,     # "info" | "warning" | "error"
  "message": str,      # human-readable explanation
}
```

### Profile Data Structure
See PRD.md FR6-FR9 for complete profile structure specification.

## Progress Notes

### Saturday Implementation - COMPLETED ✅

All Saturday tasks have been successfully completed and tested!

#### ✅ Phase 1: Core Profiling Engine (profiling.py)
- Implemented `profile_dataframe(df)` function
- Dataset-level stats: rows, columns, memory usage
- Type inference logic working for all types (numeric, datetime, boolean, categorical, text, unknown)
- Per-column stats: null count, missing %, unique count
- Top N values with frequencies
- Numeric statistics: min, max, mean, median, std, percentiles
- Datetime statistics: min, max dates
- Datetime string detection for object columns

#### ✅ Phase 2: Quality Flags Module (quality.py)
- Created quality.py with `generate_quality_flags()` function
- All quality flag rules implemented and tested:
  - HIGH_MISSING (≥30% missing) ✓
  - CONSTANT_COLUMN (single unique value) ✓
  - DOMINANT_VALUE (≥95% one value) ✓
  - HIGH_CARDINALITY_CATEGORICAL (>1000 unique) ✓
  - POTENTIAL_ID_COLUMN (>90% unique + ID-like name) ✓

#### ✅ Phase 3: Export Utilities (export_utils.py)
- Implemented `profile_to_summary_df()` to flatten profile structure
- Formats top values, quality flags, numeric stats, and datetime ranges
- Ready for CSV export

#### ✅ Phase 4: UI Integration (app.py)
- Integrated profiling engine into Streamlit UI
- Dataset summary with metrics (rows, columns, memory)
- Column summary table displaying all profile data
- CSV export download button
- Raw data preview in collapsible expander
- Loading spinners for better UX

#### ✅ Phase 5: Testing
- Tested with sample_data.csv (mixed types, missing values) ✓
- Tested with sample_products.xlsx (numeric stats, Excel format) ✓
- Created quality_flags_test.csv to verify all flag rules ✓
- All quality flags triggering correctly ✓
- Type inference working accurately ✓

## Review Summary

### What Was Accomplished
Saturday's work plan was fully completed. The core profiling engine is functional with:
- Complete type inference system
- Comprehensive statistics for numeric and datetime columns
- Quality flag detection for 5 key data quality issues
- Clean UI integration with export functionality
- All modules tested and working

### Files Created/Modified
- ✅ profiling.py (new - 214 lines)
- ✅ quality.py (new - 85 lines)
- ✅ export_utils.py (new - 127 lines)
- ✅ app.py (updated with profiling integration)
- ✅ requirements.txt (updated)
- ✅ test_data/quality_flags_test.csv (new test file)

### Key Technical Decisions
1. **Type Inference**: Used 5% uniqueness ratio to distinguish categorical from text
2. **Datetime Detection**: Sample up to 100 values for performance, require >50% parse success
3. **Quality Flags**: Simple, rule-based with clear severity levels
4. **Export Format**: Flattened structure with human-readable formatting

### Known Issues/Notes
- pandas datetime parsing warnings (harmless - expected when testing object columns)
- Memory usage calculation uses `deep=True` which can be slow on very large files (acceptable tradeoff for accuracy)

### Next Steps (Sunday Tasks)
According to the PRD weekend plan, Sunday should focus on:
1. Refining quality flags (consider adding MIXED_TYPES detection)
2. UI/UX improvements (styling, better flag display)
3. Additional export options (JSON export)
4. More comprehensive testing with realistic datasets
5. Documentation (README.md)
6. Code cleanup and comments

### MVP Status
**Saturday milestone: COMPLETE** ✅

All core functionality is working:
- ✅ File upload (CSV/Excel)
- ✅ Dataset profiling with type inference
- ✅ Quality flag detection
- ✅ Column summary display
- ✅ CSV export
- ✅ Tested with multiple datasets
