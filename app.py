"""
Data Profiler - Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import json
from io_utils import load_file
from profiling import profile_dataframe, _add_examples_to_flags
from quality import generate_quality_flags, generate_dataset_quality_flags
from export_utils import profile_to_summary_df, dataset_summary_to_dict


# Page configuration
st.set_page_config(
    page_title="Data Profiler",
    page_icon="📊",
    layout="wide"
)

# App title and description
st.title("📊 Data Profiler")
st.markdown("""
Upload a CSV or Excel file to get an instant data quality profile report.
Perfect for initial data exploration and quality assessment.
""")

# Sidebar with file uploader and settings
with st.sidebar:
    st.header("Upload Data")
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload a CSV or Excel file (up to ~50MB)"
    )

    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")
        st.info(f"Size: {uploaded_file.size / 1024:.2f} KB")

    st.header("Settings")

    null_threshold = st.slider(
        "Null value threshold (%)",
        min_value=0,
        max_value=100,
        value=10,
        help="Flag columns with null values at or above this percentage as potentially unsuitable"
    )

    top_n_values = st.slider(
        "Top N values to display",
        min_value=3,
        max_value=10,
        value=5,
        help="Number of most frequent values to show per column"
    )

    show_column_details = st.checkbox(
        "Show detailed column stats",
        value=False,
        help="Display expandable sections with full statistics for each column"
    )

# Main content area
if uploaded_file is None:
    st.info("👈 Upload a file using the sidebar to get started")
else:
    try:
        # Load the file
        with st.spinner("Loading file..."):
            df = load_file(uploaded_file)

        # Profile the dataframe
        with st.spinner("Profiling dataset..."):
            profile = profile_dataframe(df)

            # Add quality flags to each column
            for col_name, col_profile in profile["columns"].items():
                # Generate base flags (without examples)
                flags = generate_quality_flags(col_name, col_profile, profile["dataset"]["n_rows"], null_threshold)

                # Add examples to flags
                flags_with_examples = _add_examples_to_flags(flags, df[col_name], col_profile)

                col_profile["quality_flags"] = flags_with_examples

        st.success(f"Successfully profiled {len(df):,} rows and {len(df.columns)} columns")

        # Dataset Summary Section
        st.header("📋 Dataset Summary")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", f"{profile['dataset']['n_rows']:,}")
        with col2:
            st.metric("Columns", profile['dataset']['n_columns'])
        with col3:
            memory_mb = profile['dataset']['memory_usage_bytes'] / (1024 * 1024)
            st.metric("Memory Usage", f"{memory_mb:.2f} MB")

        # Duplicate Analysis Section
        dup_analysis = profile['dataset'].get('duplicate_analysis')
        if dup_analysis and dup_analysis.get('unique_rows', -1) >= 0:
            st.subheader("🔄 Duplicate Analysis")

            dup_col1, dup_col2, dup_col3 = st.columns(3)
            with dup_col1:
                st.metric("Unique Rows", f"{dup_analysis['unique_rows']:,}")
            with dup_col2:
                st.metric("Duplicate Rows", f"{dup_analysis['duplicate_rows']:,}")
            with dup_col3:
                st.metric("Duplicate %", f"{dup_analysis['duplicate_pct']:.1f}%")

            # Dataset-level quality flags
            dataset_flags = generate_dataset_quality_flags(profile['dataset'])

            if dataset_flags:
                for flag in dataset_flags:
                    if flag["severity"] == "warning":
                        st.warning(f"⚠️ **{flag['code']}**: {flag['message']}")
                    else:
                        st.info(f"ℹ️ **{flag['code']}**: {flag['message']}")

            # Show duplicate examples
            if dup_analysis.get('duplicate_sets'):
                with st.expander(f"View Duplicate Sets ({len(dup_analysis['duplicate_sets'])} shown)"):
                    for i, dup_set in enumerate(dup_analysis['duplicate_sets'], 1):
                        st.markdown(f"**Set {i}: Appears {dup_set['count']} times**")
                        st.caption(f"Example rows: {', '.join(map(str, dup_set['example_indices']))}")

                        # Display row data as JSON
                        st.json(dup_set['row_data'])
                        st.divider()
        elif dup_analysis and dup_analysis.get('error'):
            st.warning(f"⚠️ Duplicate detection: {dup_analysis['error']}")

        # Column Summary Table
        st.header("📊 Column Profile Summary")

        summary_df = profile_to_summary_df(profile)

        # Apply conditional highlighting for high null percentages
        def highlight_high_nulls(row):
            if row['Missing %'] >= null_threshold:
                return ['background-color: yellow'] * len(row)
            return [''] * len(row)

        styled_df = summary_df.style.apply(highlight_high_nulls, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        # Detailed column views (if enabled)
        if show_column_details:
            st.header("📑 Detailed Column Statistics")

            for col_name, col_profile in profile["columns"].items():
                with st.expander(f"📌 {col_name}"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Type", col_profile["inferred_type"])
                        st.metric("Missing %", f"{col_profile['missing_pct']:.1f}%")

                    with col2:
                        st.metric("Unique Count", f"{col_profile['unique_count']:,}")
                        st.metric("Non-Null", f"{col_profile['non_null_count']:,}")

                    with col3:
                        st.metric("Pandas Type", col_profile["pandas_dtype"])
                        st.metric("Null Count", f"{col_profile['null_count']:,}")

                    # Quality flags with color coding
                    if col_profile["quality_flags"]:
                        st.subheader("⚠️ Quality Flags")
                        for flag in col_profile["quality_flags"]:
                            # Display flag with severity color
                            if flag["severity"] == "error":
                                st.error(f"**{flag['code']}**: {flag['message']}")
                            elif flag["severity"] == "warning":
                                st.warning(f"**{flag['code']}**: {flag['message']}")
                            else:
                                st.info(f"**{flag['code']}**: {flag['message']}")

                            # Display examples if available
                            if flag.get("examples"):
                                with st.expander(f"View Examples ({len(flag['examples'])} shown)"):
                                    for ex in flag["examples"]:
                                        if ex['value'] == "NULL":
                                            st.text(f"Row {ex['row_number']}: [NULL value]")
                                        else:
                                            st.text(f"Row {ex['row_number']}: {ex['value']}")

                    # Top values
                    if col_profile["top_values"]:
                        st.subheader("🔝 Top Values")
                        top_df = pd.DataFrame(col_profile["top_values"])
                        st.dataframe(top_df, use_container_width=True, hide_index=True)

                    # Numeric statistics
                    if col_profile["numeric_stats"]:
                        st.subheader("📈 Numeric Statistics")
                        stats = col_profile["numeric_stats"]
                        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)

                        with stats_col1:
                            st.metric("Min", f"{stats['min']:.2f}" if stats['min'] is not None else "N/A")
                            st.metric("Mean", f"{stats['mean']:.2f}" if stats['mean'] is not None else "N/A")

                        with stats_col2:
                            st.metric("Median", f"{stats['median']:.2f}" if stats['median'] is not None else "N/A")
                            st.metric("Std Dev", f"{stats['std']:.2f}" if stats['std'] is not None else "N/A")

                        with stats_col3:
                            st.metric("Max", f"{stats['max']:.2f}" if stats['max'] is not None else "N/A")
                            st.metric("P75", f"{stats['p75']:.2f}" if stats['p75'] is not None else "N/A")

                        with stats_col4:
                            st.metric("Skewness", f"{stats['skewness']:.2f}" if stats['skewness'] is not None else "N/A")
                            if stats.get('zero_count') is not None and stats['zero_count'] > 0:
                                st.metric("Zeros", f"{stats['zero_count']:,} ({stats['zero_pct']:.1f}%)")
                            if stats.get('negative_count') is not None and stats['negative_count'] > 0:
                                st.metric("Negatives", f"{stats['negative_count']:,} ({stats['negative_pct']:.1f}%)")

                    # Datetime statistics
                    if col_profile["datetime_stats"]:
                        st.subheader("📅 Datetime Range")
                        dt_stats = col_profile["datetime_stats"]
                        dt_col1, dt_col2 = st.columns(2)

                        with dt_col1:
                            st.metric("Min Date", dt_stats['min'] if dt_stats['min'] else "N/A")

                        with dt_col2:
                            st.metric("Max Date", dt_stats['max'] if dt_stats['max'] else "N/A")

                        # Future dates warning
                        if dt_stats.get('future_count', 0) > 0:
                            st.warning(f"⚠️ Contains {dt_stats['future_count']:,} future dates ({dt_stats['future_pct']:.1f}%)")
                            st.caption(f"Latest future date: {dt_stats.get('max_future_date', 'N/A')}")

                    # String quality analysis
                    if col_profile.get("string_quality"):
                        st.subheader("🔤 String Quality Analysis")
                        sq = col_profile["string_quality"]
                        sq_col1, sq_col2 = st.columns(2)

                        with sq_col1:
                            st.metric("Whitespace Issues",
                                     f"{sq['whitespace_count']:,} ({sq['whitespace_pct']:.1f}%)")
                            st.metric("Placeholder Values",
                                     f"{sq['placeholder_count']:,} ({sq['placeholder_pct']:.1f}%)")
                            if sq['placeholder_values']:
                                st.caption(f"Found: {', '.join(sq['placeholder_values'][:3])}")

                        with sq_col2:
                            st.metric("Casing Issues", "Yes" if sq['casing_issues'] else "No")
                            if sq['casing_issues']:
                                st.caption(f"{sq['casing_groups']} groups with variants")
                            st.metric("Special Characters",
                                     f"{sq['special_char_count']:,} ({sq['special_char_pct']:.1f}%)")

        # Export functionality
        st.header("💾 Export Profile")

        col1, col2, col3 = st.columns(3)

        with col1:
            csv_data = summary_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Download Column Summary (CSV)",
                data=csv_data,
                file_name=f"{uploaded_file.name}_column_profile.csv",
                mime="text/csv",
                help="Download the column profile summary as a CSV file",
                use_container_width=True
            )

        with col2:
            # Export dataset summary
            dataset_summary = dataset_summary_to_dict(profile)
            dataset_df = pd.DataFrame([dataset_summary])
            dataset_csv = dataset_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📊 Download Dataset Summary (CSV)",
                data=dataset_csv,
                file_name=f"{uploaded_file.name}_dataset_summary.csv",
                mime="text/csv",
                help="Download dataset summary including duplicate analysis",
                use_container_width=True
            )

        with col3:
            json_data = json.dumps(profile, indent=2).encode('utf-8')
            st.download_button(
                label="📋 Download Full Profile (JSON)",
                data=json_data,
                file_name=f"{uploaded_file.name}_full_profile.json",
                mime="application/json",
                help="Download the complete profile structure as JSON",
                use_container_width=True
            )

        # Data preview (collapsed by default)
        with st.expander("🔍 View Raw Data Preview"):
            st.dataframe(df.head(20), use_container_width=True)

    except ValueError as e:
        st.error(f"Error: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        st.info("Please try a different file or check that the file is not corrupted.")
