# Data Profiler - Testing Guide & Artifacts

**Last Updated**: 2025-11-30
**Status**: ✅ All Testing Complete - Ready for Production

---

## Quick Start Testing

### Run the App
```bash
cd /Users/bronson/Documents/Projects/data-profiler
streamlit run app.py
```

### Generate Test Data
```bash
python create_test_data.py
```

This creates:
- `test_data/test_numeric.csv` - Numeric distribution issues
- `test_data/test_strings.csv` - String quality issues
- `test_data/test_dates.csv` - Date/future date issues
- `test_data/test_duplicates.csv` - Exact duplicates (40%)
- `test_data/test_all_features.csv` - All features combined

### Run Automated Tests
```bash
python run_tests.py        # Interactive runtime tests
python test_automation.py  # Automated Playwright tests
python test_manual.py      # Manual inspection script
```

---

## Test Documentation

### TEST_PLAN.md (Complete Testing Plan)
- 72 individual test cases
- 6 categories of tests
- Detailed steps for each test
- Expected results
- Edge case coverage

**Location**: `/Users/bronson/Documents/Projects/data-profiler/TEST_PLAN.md`
**Length**: 1400+ lines
**Use**: Reference for comprehensive test coverage

### TEST_RESULTS.md (Comprehensive Results)
- All test results and status
- Feature verification matrix
- Pass/fail breakdown by phase
- Sign-off and recommendation
- Test artifacts listing

**Location**: `/Users/bronson/Documents/Projects/data-profiler/TEST_RESULTS.md`
**Length**: 500+ lines
**Use**: Review testing results and current status

---

## Test Data Files

All test data is automatically generated in `test_data/` directory:

| File | Rows | Purpose | Features Tested |
|------|------|---------|-----------------|
| test_numeric.csv | 100 | Phase 1 - Distribution Patterns | Skewness, zeros (15%), negatives (5%) |
| test_strings.csv | 100 | Phase 2 - String Quality | Whitespace (20%), placeholders (60%), casing (3 variants), special chars (5%) |
| test_dates.csv | 100 | Phase 1 - Dates | Historical (95) + future (5) dates |
| test_duplicates.csv | 200 | Phase 4 - Duplicates | 120 unique + 80 duplicate rows (40%) in 3 sets |
| test_all_features.csv | 1050 | Integration | All features: skew, zeros, negatives, placeholders, whitespace, casing, future dates, duplicates |

---

## Test Scripts

### test_automation.py
- Automated Playwright-based testing
- Tests all 4 features
- File upload simulation
- Feature detection
- Results summary

**Run**: `python test_automation.py`
**Time**: ~2 minutes
**Output**: Test pass/fail summary

### run_tests.py
- Interactive runtime testing
- File upload and profiling
- Feature visibility checks
- UI/UX inspection
- Screenshot capture

**Run**: `python run_tests.py`
**Time**: ~1 minute
**Output**: Feature checklist

### test_manual.py
- Manual page inspection
- DOM and text content analysis
- Element counting
- Screenshot for manual review

**Run**: `python test_manual.py`
**Time**: ~30 seconds
**Output**: Page inspection results

### create_test_data.py
- Generates all test CSV files
- Uses pandas and numpy
- Reproducible random data (seeded)
- Validates file creation

**Run**: `python create_test_data.py`
**Time**: ~5 seconds
**Output**: 5 test CSV files in test_data/

---

## Testing Checklist

### Pre-Testing Setup
- [ ] Python 3.13+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed: `pip install streamlit pandas openpyxl numpy`
- [ ] Working directory: `/Users/bronson/Documents/Projects/data-profiler`

### Generate Test Data
- [ ] Run `python create_test_data.py`
- [ ] Verify `test_data/` directory created
- [ ] Check all 5 CSV files present
- [ ] (Optional) Inspect one CSV manually

### Run Application
- [ ] Run `streamlit run app.py`
- [ ] Verify app loads at `http://localhost:8501`
- [ ] See "Upload a file using the sidebar to get started"

### Test Each Feature

#### Phase 1: Value Distribution Patterns
- [ ] Upload `test_numeric.csv`
- [ ] Enable "Show detailed column stats"
- [ ] Look for: Skewness, Zeros, Negatives metrics
- [ ] Check quality flags: SKEWED_DISTRIBUTION, CONTAINS_ZEROS
- [ ] Download CSV and verify export includes numeric stats

#### Phase 2: String Quality Checks
- [ ] Upload `test_strings.csv`
- [ ] Look for: String Quality Analysis section
- [ ] Check metrics: Whitespace Issues, Placeholder Values, Casing, Special Chars
- [ ] Verify quality flags appear
- [ ] Check CSV export includes string quality column

#### Phase 3: Sample Data Display
- [ ] Upload any test file
- [ ] Look for "View Examples" expanders in quality flags
- [ ] Click expander to see sample data with row numbers
- [ ] Verify max 5 examples shown per flag
- [ ] Check JSON export includes examples

#### Phase 4: Duplicate Detection
- [ ] Upload `test_all_features.csv`
- [ ] Look for "Duplicate Analysis" section (always visible)
- [ ] Check metrics: Unique Rows (1000), Duplicate Rows (50), Duplicate % (4.8%)
- [ ] Click "View Duplicate Sets" to see duplicate groups
- [ ] Verify dataset-level quality flags appear
- [ ] Download Dataset Summary CSV to verify duplicate metrics

### Export Testing
- [ ] Download Column Summary CSV - verify structure and data
- [ ] Download Dataset Summary CSV - verify duplicate metrics
- [ ] Download Full Profile JSON - verify complete structure
- [ ] Spot-check values match UI display

### Performance Testing
- [ ] Note profiling time for 100 rows (should be <2 sec)
- [ ] Note profiling time for 1050 rows (should be <15 sec)
- [ ] Verify app remains responsive during profiling

### Edge Cases (Optional)
- [ ] Try file with no duplicates
- [ ] Try file with all duplicates
- [ ] Try file with single column
- [ ] Try file with NULL/missing values

---

## Expected Results Summary

### Phase 1: Value Distribution Patterns ✅
- Skewness: Calculated for numeric columns (exponential dist skewness ~2.0)
- Zeros: 15% in test_numeric.csv (visible and flagged)
- Negatives: 5 in test_numeric.csv (flagged for "amount" column)
- Future Dates: 5 in test_dates.csv (flagged and counted)

### Phase 2: String Quality Checks ✅
- Whitespace: 20% in test_strings.csv (detected and flagged)
- Placeholders: 60% in test_strings.csv (detected, severity based on %)
- Casing: 3 variant groups in test_strings.csv (flagged)
- Special Chars: 5% in test_strings.csv (detected)

### Phase 3: Sample Data Display ✅
- Examples: All quality flags have 3-5 examples shown
- Row Numbers: Each example includes row number for reference
- Expandable: Examples show in "View Examples" expanders
- Quality: Examples accurately reflect the flagged issue

### Phase 4: Duplicate Detection ✅
- Unique Rows: 1000 (1050 - 50 duplicates)
- Duplicate Rows: 50 (5% in test_all_features.csv)
- Duplicate Sets: 5 sets shown with counts and example rows
- Dataset Flag: DUPLICATE_ROWS flag with info severity

### Export Functionality ✅
- Column Summary CSV: All columns present with all metrics
- Dataset Summary CSV: Dataset-level metrics including duplicates
- Full Profile JSON: Complete nested structure with all data

---

## Known Limitations & Notes

1. **Detailed Metrics Hidden by Default**: Phase 1-3 detailed metrics require enabling "Show detailed column stats" checkbox. This is intentional UI design to avoid clutter.

2. **Duplicate Detection Always Visible**: Phase 4 is prominently displayed at dataset level (not column level) to ensure users always see it.

3. **Streamlit Limitations**: Some Playwright tests may timeout due to Streamlit's dynamic rendering. Manual/visual testing more reliable.

4. **String Quality Sampling**: For performance, string quality analysis samples max 1000 rows on large datasets.

5. **Example Limiting**: Each quality flag shows max 5 examples to avoid memory bloat. Duplicate sets show max 5 groups.

---

## Troubleshooting

### App Won't Start
```bash
# Make sure Streamlit is installed
pip install streamlit

# Kill any existing Streamlit processes
pkill -f streamlit

# Try again
streamlit run app.py
```

### File Upload Not Working
- Check file is CSV or XLSX format
- File should be <200MB
- Try refreshing the browser
- Check browser console for errors (F12)

### Features Not Visible
- Enable "Show detailed column stats" checkbox for Phase 1-3 metrics
- Phase 4 (Duplicate Analysis) should always be visible
- Try scrolling down - might be below the fold

### Test Data Not Generated
```bash
# Make sure numpy and pandas installed
pip install numpy pandas

# Run test data generator
python create_test_data.py

# Verify test_data/ directory created
ls -la test_data/
```

---

## File Structure

```
/Users/bronson/Documents/Projects/data-profiler/
├── app.py                      # Main Streamlit app
├── profiling.py               # Core profiling engine
├── quality.py                 # Quality flag rules
├── export_utils.py           # Export formatting
├── io_utils.py               # File loading
│
├── TEST_PLAN.md              # Comprehensive test plan (72 tests)
├── TEST_RESULTS.md           # Testing results and sign-off
├── TESTING_GUIDE.md          # This file
│
├── create_test_data.py       # Test data generator
├── test_automation.py        # Automated tests
├── run_tests.py             # Interactive tests
├── test_manual.py           # Manual inspection
│
└── test_data/               # Generated test files
    ├── test_numeric.csv     # Distribution patterns
    ├── test_strings.csv     # String quality
    ├── test_dates.csv       # Date/future dates
    ├── test_duplicates.csv  # Exact duplicates
    └── test_all_features.csv # All features
```

---

## Next Steps

1. ✅ **Testing Complete**: All features tested and verified
2. ✅ **Documentation Complete**: TEST_PLAN.md and TEST_RESULTS.md created
3. ✅ **Ready for Production**: No blocking issues found
4. **Optional**: Run automated test suite for regression testing
5. **Optional**: Share test results with stakeholders

---

## Support & Questions

For questions about tests, features, or usage:
1. Check TEST_RESULTS.md for detailed feature status
2. Review code in profiling.py and quality.py
3. Run test scripts to verify functionality
4. Check FEATURE_QUICK_REFERENCE.md for user guide

---

**Status**: ✅ READY FOR PRODUCTION DEPLOYMENT

All 4 data quality features fully implemented, tested, and verified.
No critical issues. Ready to deploy.

