from __future__ import annotations

from typing import Iterable, Sequence

import pandas as pd
import requests

from .splitter import add_rows_with_split_data
from .url_checker import check_url_status


def filter_rows_with_any_value(df: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    """
    Keep rows where at least one target column is non-empty.
    """
    mask = False
    for col in columns:
        if col in df.columns:
            col_mask = df[col].notna() & (df[col].astype(str).str.strip() != "")
            mask = mask | col_mask
    return df.loc[mask].copy()


def split_columns_to_rows(df: pd.DataFrame, columns: Sequence[str], delimiter: str = ";") -> pd.DataFrame:
    """
    Apply row splitting for multiple columns in sequence.
    """
    out = df.copy()
    for col in columns:
        if col in out.columns:
            out = add_rows_with_split_data(out, col, delimiter)
    return out


def process_url_column(
    df: pd.DataFrame,
    column_name: str,
    delimiter: str = ";",
    retries: int = 3,
    min_delay: float = 1.2,
    max_delay: float = 2.0,
    timeout: int = 15,
    verify_ssl: bool = True,
) -> pd.DataFrame:
    """
    Check URLs in one column and append result columns.
    """
    out = df.copy()
    working_urls = []
    accepted_urls = []
    error_404_urls = []
    ratelimited_urls = []
    broken_urls_other = []
    status_details = []

    session = requests.Session()

    total_rows = len(out)
    for idx, value in enumerate(out[column_name].fillna("").astype(str), start=1):
        print(f"[{idx}/{total_rows}] Checking {column_name}...")

        urls = [u.strip() for u in value.split(delimiter) if u.strip()]
        working, accepted, error_404, ratelimited, broken_other, statuses = [], [], [], [], [], []

        for url in urls:
            result = check_url_status(
                url=url,
                retries=retries,
                min_delay=min_delay,
                max_delay=max_delay,
                timeout=timeout,
                verify_ssl=verify_ssl,
                session=session,
            )

            if result.status == "Working":
                working.append(result.url)
            elif result.status == "Accepted":
                accepted.append(result.url)
            elif result.status == "Rate Limited":
                ratelimited.append(result.url)
            elif result.status == "Broken-404":
                error_404.append(result.url)
            else:
                broken_other.append(result.url)

            statuses.append(result.detail)

        working_urls.append("; ".join(working))
        accepted_urls.append("; ".join(accepted))
        error_404_urls.append("; ".join(error_404))
        ratelimited_urls.append("; ".join(ratelimited))
        broken_urls_other.append("; ".join(broken_other))
        status_details.append("; ".join(statuses))

    out[f"{column_name}_Working"] = working_urls
    out[f"{column_name}_Accepted202"] = accepted_urls
    out[f"{column_name}_Error404"] = error_404_urls
    out[f"{column_name}_RateLimited429"] = ratelimited_urls
    out[f"{column_name}_BrokenOther"] = broken_urls_other
    out[f"{column_name}_StatusDetail"] = status_details

    return out