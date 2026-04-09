
---

## `examples/run_example.py`

```python
from pathlib import Path
import pandas as pd

from cgspace_url_checker.processor import (
    filter_rows_with_any_value,
    process_url_column,
    split_columns_to_rows,
)

file_path = Path(r"C:\path\to\cgspace_metadata_no_split.csv")
output_dir = Path(r"C:\path\to\output")
output_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(file_path, dtype=str)

url_columns = ["dcterms.relation", "cg.identifier.url"]

df = filter_rows_with_any_value(df, url_columns)
df = split_columns_to_rows(df, url_columns, delimiter=";")

for col in url_columns:
    if col in df.columns:
        df = process_url_column(df, col)

df.to_csv(output_dir / "checked_output.csv", index=False, encoding="utf-8-sig")