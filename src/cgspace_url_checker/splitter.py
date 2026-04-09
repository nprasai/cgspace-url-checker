from __future__ import annotations

import pandas as pd


def add_rows_with_split_data(df: pd.DataFrame, column_name: str, delimiter: str = ";") -> pd.DataFrame:
    """
    Split delimited values in a column into separate rows while preserving other columns.
    """
    if column_name not in df.columns:
        return df.copy()

    df = df.copy()

    # Normalize values
    split_series = (
        df[column_name]
        .fillna("")
        .astype(str)
        .apply(lambda x: [item.strip() for item in x.split(delimiter) if item.strip()] or [""])
    )

    exploded = df.assign(**{column_name: split_series}).explode(column_name, ignore_index=True)
    return exploded