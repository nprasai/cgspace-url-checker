# CGSpace URL Checker
A lightweight Python tool to identify working and non-working URLS in CGSpace metadata fields. 
This tool is designed to support data quality checks, repository maintenance by identifying broken or problematic links
in metadata fields such as : (dcterms.relation, cg.identifier.url)

This tool helps you:
- split multi-value URL fields often separated by delimiter such as ";" into separate rows
- validate each URL using HTTP status checks
- categorize URLs into:
      Working (200)
      Accepted (202)
      Broken (404)
      Rate-limited (429)
      Other client/server errors
- export clean, structured outputs for analysis 

## Installation

```bash
pip install -e .

##Run
### Step 1: Go to folder
```bash
cd cgspace_url_checker
### Step 2: Install locally
```bash
pip install -e .

### Step 3:
```bash
cgspace-url-checker \
  --input "your_file.csv" \
  --output-dir "output_folder"
### Optional Arguments
```bash
--url-columns dcterms.relation cg.identifier.url
--delimiter ";"
--retries 3
--timeout 15
--verify-ssl

##Run inside Python
```Python
from cgspace_url_checker.processor import (
    filter_rows_with_any_value,
    process_url_column,
    split_columns_to_rows,
)

import pandas as pd

df = pd.read_csv("input.csv", dtype=str)

url_columns = ["dcterms.relation", "cg.identifier.url"]

df = filter_rows_with_any_value(df, url_columns)
df = split_columns_to_rows(df, url_columns)

for col in url_columns:
    df = process_url_column(df, col)

df.to_csv("output.csv", index=False)
