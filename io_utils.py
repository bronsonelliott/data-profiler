"""
File loading utilities for CSV and Excel files.
"""

import pandas as pd
from typing import Optional


def load_file(uploaded_file) -> pd.DataFrame:
    """
    Load a CSV or Excel file into a pandas DataFrame.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        pd.DataFrame: Loaded data

    Raises:
        ValueError: If file format is unsupported or file cannot be read
    """
    if uploaded_file is None:
        raise ValueError("No file provided")

    # Get file extension
    file_name = uploaded_file.name
    file_extension = file_name.lower().split('.')[-1]

    try:
        if file_extension == 'csv':
            # Try UTF-8 first, fall back to latin1 if needed
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8', low_memory=False)
            except UnicodeDecodeError:
                # Reset file pointer and try latin1
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='latin1', low_memory=False)

        elif file_extension in ['xlsx', 'xls']:
            # Read first sheet only
            df = pd.read_excel(uploaded_file, sheet_name=0)

        else:
            raise ValueError(f"Unsupported file format: .{file_extension}. Please upload a CSV or Excel file.")

        # Check if dataframe is empty
        if df.empty:
            raise ValueError("The uploaded file is empty")

        return df

    except ValueError:
        # Re-raise ValueError as-is (our custom error messages)
        raise
    except Exception as e:
        # Catch any other errors (corrupt files, parsing errors, etc.)
        raise ValueError(f"Error reading file: {str(e)}")
