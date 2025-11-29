# **CSV/Excel Data Profiler – Product Requirements Document (PRD)**

## **1\. Overview**

**Product name:** CSV/Excel Data Profiler  
**Goal:** A lightweight local web app that lets an analyst upload a CSV or Excel file and instantly see a comprehensive data quality/profile report.

**Primary users:**

* Data analysts / BI professionals who frequently receive new datasets  
* Use cases: pre‑profiling datasets before loading into BI tools, ETL, or ad‑hoc analysis

### **Problem**

Initial data exploration is repetitive and error‑prone:

* Writing similar pandas scripts to check column types, missingness, and basic stats  
* Manually exploring in Excel to find obvious issues  
* No standardized, shareable profile of data quality

### **Solution**

A simple Streamlit app that:

* Accepts CSV/XLSX uploads  
* Profiles the dataset with pandas  
* Presents a clear, tabular data quality report  
* Flags potential issues (missingness, IDs, high cardinality, mixed types)

### **Success Criteria for Weekend MVP**

By Sunday evening:

* Run `streamlit run app.py` locally  
* Upload a CSV or Excel file (≤ \~50MB)  
* See:  
  * Dataset summary (rows, columns, memory)  
  * Per‑column summary with type, missing %, unique count, top values  
  * Simple data quality flags for each column  
* Download column summary as CSV  
* App handles at least 2–3 different sample datasets without crashing

---

## **2\. Scope**

### **2.1 In Scope (MVP)**

1. **File upload / ingestion**  
   * Upload CSV or Excel (`.xlsx`) from local machine  
   * Soft file size limit around 50MB (configurable)  
   * For Excel, use first sheet (no sheet picker needed for MVP)  
   * Basic error handling for unsupported or corrupt files  
2. **Dataset overview**  
   * Number of rows and columns  
   * Estimated memory usage  
   * Optional: load time display  
3. **Per‑column profiling** For each column:  
   * Column name  
   * Pandas dtype  
   * Inferred high‑level type (numeric, datetime, boolean, categorical, text, unknown)  
   * Non‑null count  
   * Null count and % missing  
   * Unique count (cardinality)  
   * Top N values (e.g., top 5\) with counts and % of rows  
4. Additional per‑type stats:  
   * **Numeric columns**  
     * min, max  
     * mean, median  
     * standard deviation  
     * 25th, 50th, 75th percentiles  
   * **Datetime columns**  
     * min date  
     * max date  
   * **Categorical/text columns**  
     * unique count  
     * top N categories \+ frequencies  
5. **Data quality flags (MVP level)** Simple, rule‑based flags on each column:  
   * High missingness (e.g., missing % ≥ 30%)  
   * Constant or near‑constant values  
   * High cardinality in categorical/text columns  
   * Potential ID columns (very high uniqueness, name looks like ID)  
   * Mixed types in a column  
   * Optional: datetime parsing issues (if implemented)  
6. Each flag should have a structured representation:  
   * `code` (machine‑readable)  
   * `severity` (`info` / `warning` / `error`)  
   * `message` (human explanation)  
7. **Report presentation (UI)**  
   * Built in Streamlit  
   * Layout:  
     * Sidebar: file uploader and simple settings  
     * Main area:  
       * Dataset summary section  
       * Column summary table (one row per column)  
       * Optional per‑column detail via expanders  
8. **Export**  
   * Download column summary table as CSV using `st.download_button`  
   * Optional stretch: JSON export of full profile structure

### **2.2 Out of Scope (for this MVP)**

* Authentication or multi‑user features  
* Database connections (CSV/XLSX only)  
* Scheduled or automated profiling  
* Data cleaning / fixing operations  
* Advanced statistical tests or ML‑based anomaly detection  
* Rich visualizations beyond simple tables (histograms can be a stretch)  
* Full ydata‑profiling integration (consider as a later stretch goal)

---

## **3\. User Stories**

1. **Initial dataset understanding**  
   As a data analyst, I want to upload a CSV/Excel file and immediately see how many rows and columns it has and how much data it contains.  
2. **Column‑level insight**  
   As a data analyst, I want to see inferred data types, missingness, and basic stats for each column so I can decide how to use them.  
3. **Surface data issues**  
   As a data analyst, I want obvious data quality issues (e.g., high missingness, high cardinality, ID‑like columns) automatically flagged so I can prioritize cleaning.  
4. **Shareable documentation**  
   As a data analyst, I want to export a summary report (CSV) so I can attach it to tickets, documentation, or send to stakeholders.  
5. **Fast feedback loop**  
   As a data analyst, I want the profile to run within a few seconds on typical BI‑sized datasets so it fits into my normal workflow.

---

## **4\. Functional Requirements**

### **4.1 File Upload & Ingestion**

**FR1:** User can upload a file via a Streamlit `st.file_uploader` supporting:

* `.csv`  
* `.xlsx`

**FR2:** File type detection:

* Use file extension to decide:  
  * CSV → `pandas.read_csv`  
  * XLSX → `pandas.read_excel` (first sheet)

**FR3:** If loading fails (wrong format, encoding error, corrupt file), show a clear error message in the UI.

**FR4:** Implement `load_file(uploaded_file)` helper:

\# io\_utils.py  
def load\_file(uploaded\_file) \-\> pd.DataFrame:  
    """  
    Take a Streamlit UploadedFile and return a pandas DataFrame.  
    Handles CSV and XLSX, raises or logs informative errors.  
    """

### **4.2 Dataset Overview**

**FR5:** After loading, compute and display:

* Number of rows: `df.shape[0]`  
* Number of columns: `df.shape[1]`  
* Estimated memory usage: `df.memory_usage(deep=True).sum()` (formatted in KB/MB)  
* Optionally, file size if available from `uploaded_file.size`

### **4.3 Column Profiling**

Implement a core profiling function returning a structured dict.

\# profiling.py  
def profile\_dataframe(df: pd.DataFrame) \-\> dict:  
    """  
    Returns a structured profile for the dataframe.

    {  
      "dataset": {  
        "n\_rows": int,  
        "n\_columns": int,  
        "memory\_usage\_bytes": int,  
      },  
      "columns": {  
        column\_name: {  
          "pandas\_dtype": str,  
          "inferred\_type": str,        \# one of: numeric, datetime, boolean, categorical, text, unknown  
          "non\_null\_count": int,  
          "null\_count": int,  
          "missing\_pct": float,        \# 0–100  
          "unique\_count": int,  
          "top\_values": \[              \# list of top N values  
            {"value": \<repr\>, "count": int, "pct": float},  
            ...  
          \],  
          "numeric\_stats": {           \# or None  
             "min": float,  
             "max": float,  
             "mean": float,  
             "median": float,  
             "std": float,  
             "p25": float,  
             "p50": float,  
             "p75": float,  
          } or None,  
          "datetime\_stats": {          \# or None  
             "min": str,               \# ISO date/time  
             "max": str,  
          } or None,  
          "quality\_flags": \[           \# filled in by quality module  
             \# list of flag dicts  
          \],  
        },  
        ...  
      }  
    }  
    """

**FR6:** Inferred type:

* Map pandas dtypes to simplified types:  
  * numeric: `int*`, `float*`  
  * datetime: `datetime64[ns]`  
  * boolean: `bool`  
  * otherwise: treat as `categorical` vs `text` based on heuristics:  
    * If `unique_count` is relatively small vs rows → `categorical`  
    * Otherwise → `text`  
* For `object` columns with date‑like strings, optionally test a small sample with `pd.to_datetime` to infer `datetime`.

**FR7:** For each column, compute:

* `null_count` and `non_null_count`  
* `missing_pct = null_count / len(df) * 100`  
* `unique_count = df[col].nunique(dropna=True)`  
* `top_values`: e.g. `df[col].value_counts(dropna=False).head(5)`, converted to list of dicts with value, count, and pct of rows.

**FR8:** Numeric stats (`inferred_type == "numeric"`):

* `min`, `max`, `mean`, `median`, `std`  
* 25th, 50th, 75th percentiles via `df[col].quantile([0.25, 0.5, 0.75])`

**FR9:** Datetime stats (`inferred_type == "datetime"`):

* `min` and `max` dates from `df[col].min()` / `max()` (as ISO strings)

### **4.4 Data Quality Flags**

Implement a function to generate flags from per‑column stats.

\# quality.py  
def generate\_quality\_flags(col\_name: str, col\_profile: dict, total\_rows: int) \-\> list\[dict\]:  
    """  
    Returns a list of quality flag dicts for a single column.

    Each flag:  
    {  
      "code": str,         \# e.g., "HIGH\_MISSING"  
      "severity": str,     \# "info" | "warning" | "error"  
      "message": str,      \# human-readable explanation  
    }  
    """

**FR10:** Recommended rules (thresholds can be constants):

* **HIGH\_MISSING**  
  * Condition: `missing_pct >= 30`  
  * Severity: `warning`  
  * Message: e.g., `"High missing rate: 45% of values are null"`  
* **CONSTANT\_COLUMN**  
  * Condition: `unique_count == 1`  
  * Severity: `info`  
  * Message: `"Column has a single unique value"`  
* **DOMINANT\_VALUE**  
  * Condition: top value accounts for ≥ 95% of rows  
  * Severity: `info`  
  * Message: `"One value represents 95%+ of rows"`  
* **HIGH\_CARDINALITY\_CATEGORICAL**  
  * Condition: `inferred_type` in `{categorical, text}` and `unique_count > 1000`  
  * Severity: `warning`  
  * Message: `"High cardinality categorical/text column"`  
* **POTENTIAL\_ID\_COLUMN**  
  * Condition:  
    * `unique_count / total_rows > 0.9`, and  
    * column name matches ID‑like patterns (`id`, `*_id`, `*id` case‑insensitive)  
  * Severity: `info`  
  * Message: `"Column looks like a unique identifier"`  
* **MIXED\_TYPES**  
  * Condition: pandas dtype is `object` and multiple Python types seen in a sample  
  * Severity: `warning`  
  * Message: `"Column appears to contain mixed data types"`  
* **DATETIME\_PARSING\_ISSUES** (optional)  
  * If you attempt `pd.to_datetime` on `object` column with `errors="coerce"`:  
    * High proportion of unparsable values  
  * Severity: `warning`  
  * Message: `"Many values could not be parsed as datetime"`

Attach the list returned by `generate_quality_flags` to `col_profile["quality_flags"]`.

### **4.5 UI / UX (Streamlit)**

**FR11:** Main layout:

* **Sidebar**  
  1. File uploader widget  
  2. Optional settings:  
     * Missingness threshold for highlighting (default 30%)  
     * Number of top values to show (default 5\)  
* **Main area**  
  1. Dataset summary section:  
     * File name (if available)  
     * Rows, columns, memory usage  
  2. Column summary table:  
     * One row per column with key stats  
  3. Optional: per‑column details in expanders

**FR12:** Column summary table content:

* Column name  
* Inferred type  
* Missing %  
* Unique count  
* Example top values (comma‑separated, truncated)  
* Flags → either:  
  * Combined text (e.g., `"High missing; Potential ID"`) or  
  * Count of flags with tooltip or expanded view

Implementation: create a `pandas.DataFrame` from the profile dict, then display with `st.dataframe`.

**FR13:** Per‑column detail (optional stretch):

* Use `st.expander(column_name)` to show:  
  * Full numeric/datetime stats  
  * Full table of top N values with counts and percentages  
  * Optional quick chart (e.g., histogram for numeric columns using `st.bar_chart`)

### **4.6 Exporting**

**FR14:** Summary export (MVP):

* Create helper:

\# export\_utils.py  
def profile\_to\_summary\_df(profile: dict) \-\> pd.DataFrame:  
    """  
    Flatten column profiles into a single DataFrame with one row per column.  
    """

* Use `st.download_button` to let user download this summary as CSV.

**FR15:** Stretch export:

* JSON export of the entire `profile` dict through another download button.

---

## **5\. Non‑Functional Requirements**

* **Performance**  
  * Target: Profile typical BI datasets up to \~50MB or \~1–2M rows on a laptop in under \~10 seconds.  
* **Usability**  
  * Minimal configuration; sensible defaults.  
  * Clear messages when something goes wrong (file too large, bad format).  
* **Reliability**  
  * Handle:  
    * Empty files  
    * Columns with all nulls  
    * Mixed types without crashing  
* **Maintainability**  
  * Keep logic modular:  
    * IO separate from profiling  
    * Profiling separate from quality rules  
    * UI code in `app.py` orchestrating the modules

---

## **6\. Technical Design & Structure**

### **6.1 Tech Stack**

* **Language:** Python 3.x  
* **Libraries:**  
  * `pandas` for data handling  
  * `numpy` (indirect via pandas)  
  * `streamlit` for UI  
  * `openpyxl` for Excel support  
  * Optional later: `ydata-profiling` for rich profiles

### **6.2 Suggested File Structure**

data\_profiler/  
├── app.py               \# Streamlit entrypoint  
├── profiling.py         \# profile\_dataframe and helpers  
├── quality.py           \# generate\_quality\_flags and constants  
├── io\_utils.py          \# load\_file and related helpers  
├── export\_utils.py      \# profile\_to\_summary\_df, JSON export  
├── requirements.txt  
└── PRD.md               \# this document

---

## **7\. MVP Checklist**

To consider the MVP “done”:

* \[ \] Can run `streamlit run app.py` locally  
* \[ \] Upload CSV and XLSX files  
* \[ \] See dataset summary (rows, columns, memory)  
* \[ \] See per‑column table with:  
  * Column name  
  * Pandas dtype & inferred type  
  * Missing count & %  
  * Unique count  
  * Top 5 values  
* \[ \] At least these flags working:  
  * HIGH\_MISSING  
  * CONSTANT\_COLUMN / DOMINANT\_VALUE  
  * HIGH\_CARDINALITY\_CATEGORICAL  
  * POTENTIAL\_ID\_COLUMN  
* \[ \] Download column summary as CSV  
* \[ \] Successfully profile at least:  
  * 1 mostly numeric dataset  
  * 1 mixed text/numeric dataset  
  * 1 dataset with dates and missing values

---

# **Weekend Development Plan**

You can refer to this plan while working with Claude Code. Each day builds incrementally toward the MVP.

## **Friday – Setup & Skeleton (≈2–3 hours)**

**Goal:** Project scaffolding \+ upload and preview working.

1. **Environment & project setup**  
   * Create project folder and (optionally) git repo.  
   * Create virtual environment.

Install dependencies:  
pip install streamlit pandas openpyxl

*   
  * Create `requirements.txt` from current env or manually list core libs.  
2. **Basic file structure**  
   * Create empty files:  
     * `app.py`  
     * `io_utils.py`  
     * `profiling.py`  
     * `quality.py`  
     * `export_utils.py`  
     * `PRD.md` (paste this document)  
3. **File loading \+ preview**  
   * In `io_utils.py`, implement `load_file(uploaded_file)`.  
   * In `app.py`:  
     * Add app title/description.  
     * Add `st.file_uploader` (CSV/XLSX).  
     * When file uploaded:  
       * Call `load_file`.  
       * Show shape and `st.dataframe(df.head())`.  
4. **Smoke test**  
   * Run `streamlit run app.py`.  
   * Test with a few small CSV/XLSX files.

**Example Claude Code prompt for Friday:**

“Read PRD.md. Implement `io_utils.load_file(uploaded_file)` as described, and a minimal `app.py` that uses it to upload a CSV/XLSX and display `df.head()`.”

---

## **Saturday – Profiling Engine & Summary UI (≈3–5 hours)**

**Goal:** Implement `profile_dataframe`, basic quality flags, and show column summary in UI.

1. **Implement profiling core (`profiling.py`)**  
   * Implement `profile_dataframe(df)` to:  
     * Fill `dataset` stats (`n_rows`, `n_columns`, `memory_usage_bytes`).  
     * Loop over columns and compute:  
       * pandas dtype  
       * inferred type  
       * non‑null/null counts, missing %  
       * unique count  
       * top values  
       * numeric/datetime stats where applicable  
2. **Implement quality flags (`quality.py`)**  
   * Implement `generate_quality_flags(col_name, col_profile, total_rows)`.  
   * Include at least:  
     * HIGH\_MISSING  
     * CONSTANT\_COLUMN / DOMINANT\_VALUE  
     * HIGH\_CARDINALITY\_CATEGORICAL  
     * POTENTIAL\_ID\_COLUMN  
   * Wire this into `profile_dataframe` so each column gets `quality_flags`.  
3. **Convert profile to summary DataFrame (`export_utils.py`)**  
   * Implement `profile_to_summary_df(profile)` that:  
     * Creates one row per column with:  
       * Column name  
       * Pandas dtype  
       * Inferred type  
       * Missing %  
       * Unique count  
       * Example top values  
       * Combined flags string  
4. **Integrate into Streamlit UI (`app.py`)**  
   * After loading `df`:  
     * Call `profile_dataframe(df)`.  
     * Use `profile_to_summary_df` to get a summary DataFrame.  
     * Display dataset summary metrics.  
     * Display summary DataFrame via `st.dataframe`.  
5. **Quick manual testing**  
   * Use 2–3 different test files:  
     * Mostly numeric  
     * Mixed types with some missing data  
   * Check that types, missing %, unique counts, and flags roughly match expectations.

**Example Claude Code prompts for Saturday:**

“Using the spec in PRD.md, implement `profile_dataframe(df)` in profiling.py, including the dict structure shown.”

“Now implement `generate_quality_flags` in quality.py for the HIGH\_MISSING, CONSTANT\_COLUMN, HIGH\_CARDINALITY\_CATEGORICAL, and POTENTIAL\_ID\_COLUMN rules.”

---

## **Sunday – Polishing, Extra Flags, Export & Finishing Touches (≈3–5 hours)**

**Goal:** Make it nicer to use, add export, refine flags, and wrap up.

1. **Refine flags**  
   * Add MIXED\_TYPES detection.  
   * Optionally add DATETIME\_PARSING\_ISSUES.  
   * Ensure each flag has `code`, `severity`, and readable `message`.  
   * Adjust thresholds if needed based on your test data.  
2. **Improve UI & UX**  
   * Add a “Dataset summary” section at top:  
     * Rows, columns, memory usage, file name.  
   * Highlight potential issues:  
     * For example, color missing% column in summary DataFrame via `st.dataframe` styling or just rely on flags column.  
   * Optional:  
     * Add `st.expander` per column name for detailed stats.  
3. **Export functionality**  
   * Implement CSV export in `app.py`:  
     * Use `profile_to_summary_df(profile)` → CSV bytes buffer → `st.download_button`.  
   * Optional: JSON export of the raw profile dict.  
4. **Testing with more realistic data**  
   * Test on:  
     * A BI‑style dataset with IDs, dates, categories, numeric measures.  
     * A “dirty” dataset with lots of nulls and mixed types.  
   * Confirm:  
     * The app still performs acceptably.  
     * Flags appear where you’d expect as an analyst.  
5. **Documentation & cleanup**  
   * Create a simple `README.md`:  
     * What the app does  
     * How to install and run  
     * Example use cases  
   * Light code cleanup:  
     * Remove unused imports  
     * Add comments to core functions

**Example Claude Code prompts for Sunday:**

“Refactor app.py to add a dataset summary section and a cleaner layout, using the structure described in PRD.md.”

“Implement CSV export of the column summary DataFrame via `st.download_button`.”

