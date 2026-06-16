import pandas as pd

from backend.config import FEATURE_COLUMNS, NUM_COLS


def validate_required_columns(df: pd.DataFrame):
    """
    Check whether the input dataframe contains all required model features.
    """

    missing_columns = [
        col for col in FEATURE_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        return False, missing_columns

    return True, []


def validate_numeric_columns(df: pd.DataFrame):
    """
    Convert numeric columns to numeric type and check for invalid values.
    """

    df = df.copy()

    for col in NUM_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    invalid_columns = [
        col for col in NUM_COLS
        if df[col].isnull().any()
    ]

    if invalid_columns:
        return False, invalid_columns, df

    return True, [], df


def prepare_single_input(input_data: dict):
    """
    Convert one user input dictionary into a valid dataframe for prediction.
    """

    df = pd.DataFrame([input_data])

    has_columns, missing_columns = validate_required_columns(df)

    if not has_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    is_numeric, invalid_columns, df = validate_numeric_columns(df)

    if not is_numeric:
        raise ValueError(f"Invalid or missing numeric values in: {invalid_columns}")

    return df[FEATURE_COLUMNS]


def prepare_batch_input(df: pd.DataFrame):
    """
    Validate uploaded CSV data before batch prediction.
    """

    has_columns, missing_columns = validate_required_columns(df)

    if not has_columns:
        raise ValueError(f"Uploaded file is missing required columns: {missing_columns}")

    is_numeric, invalid_columns, df = validate_numeric_columns(df)

    if not is_numeric:
        raise ValueError(f"Uploaded file has invalid or missing numeric values in: {invalid_columns}")

    return df[FEATURE_COLUMNS]