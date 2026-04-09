from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd

from .processor import filter_rows_with_any_value, process_url_column, split_columns_to_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Split and check URL columns in CGSpace metadata.")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output-dir", required=True, help="Directory for output files")
    parser.add_argument(
        "--url-columns",
        nargs="+",
        default=["dcterms.relation", "cg.identifier.url"],
        help="URL columns to process",
    )
    parser.add_argument("--delimiter", default=";", help="Delimiter used inside URL cells")
    parser.add_argument("--verify-ssl", action="store_true", help="Verify SSL certificates")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=15)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    current_date = datetime.now().strftime("%Y-%m-%d")
    split_output = output_dir / f"{input_path.stem}_split_{current_date}.csv"
    checked_output = output_dir / f"{input_path.stem}_checked_{current_date}.csv"

    df = pd.read_csv(input_path, dtype=str)

    df = filter_rows_with_any_value(df, args.url_columns)
    df = split_columns_to_rows(df, args.url_columns, delimiter=args.delimiter)
    df.to_csv(split_output, encoding="utf-8-sig", index=False)
    print(f"Saved split file: {split_output}")

    for col in args.url_columns:
        if col in df.columns:
            print(f"\nChecking URLs in column: {col}")
            df = process_url_column(
                df=df,
                column_name=col,
                delimiter=args.delimiter,
                retries=args.retries,
                timeout=args.timeout,
                verify_ssl=args.verify_ssl,
            )
        else:
            print(f"Column not found: {col}")

    df.to_csv(checked_output, encoding="utf-8-sig", index=False)
    print(f"\nDone. Saved checked file: {checked_output}")


if __name__ == "__main__":
    main()