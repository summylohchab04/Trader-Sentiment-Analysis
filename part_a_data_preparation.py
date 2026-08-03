"""
Part A — Data Preparation
Trader Performance vs Market Sentiment (Hyperliquid)

This script:
1. Loads the Fear/Greed sentiment dataset and the historical trader dataset.
2. Displays basic dataset info (shape, dtypes, head).
3. Checks for missing values and duplicate rows.
4. Removes duplicate rows if present.
5. Converts timestamp columns into proper datetime format.
6. Creates a common `Date` column (daily granularity) in both datasets.
7. Merges the two datasets on `Date`.
8. Saves the merged result as merged_data.csv.

Run with: python part_a_data_preparation.py
Expects fear_greed_index.csv and historical_data.csv in the same folder
(update FEAR_GREED_PATH / HISTORICAL_PATH below if your files live elsewhere).
"""

import pandas as pd

# ---------------------------------------------------------------------------
# 0. CONFIG — update these paths if your files are located elsewhere
# ---------------------------------------------------------------------------
FEAR_GREED_PATH = "fear_greed_index.csv"
HISTORICAL_PATH = "historical_data.csv"
OUTPUT_PATH = "merged_data.csv"

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)


def load_and_inspect(path: str, name: str) -> pd.DataFrame:
    """Load a CSV and print basic diagnostic info about it."""
    df = pd.read_csv(path)

    print(f"\n{'=' * 70}")
    print(f"DATASET: {name}  ({path})")
    print(f"{'=' * 70}")
    print(f"Shape (rows, cols): {df.shape}")

    print("\n--- Column dtypes ---")
    print(df.dtypes)

    print("\n--- First 5 rows ---")
    print(df.head())

    print("\n--- Missing values per column ---")
    missing = df.isnull().sum()
    print(missing[missing >= 0])  # show all columns, including zero-missing ones

    dup_count = df.duplicated().sum()
    print(f"\n--- Duplicate rows: {dup_count} ---")

    return df


def remove_duplicates(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """Drop fully duplicated rows, reporting how many were removed."""
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    removed = before - len(df)
    print(f"[{name}] Removed {removed} duplicate row(s). New shape: {df.shape}")
    return df


def main():
    # -----------------------------------------------------------------
    # 1. Load and inspect both datasets
    # -----------------------------------------------------------------
    fear_greed = load_and_inspect(FEAR_GREED_PATH, "Fear & Greed Index")
    trades = load_and_inspect(HISTORICAL_PATH, "Historical Trader Data")

    # -----------------------------------------------------------------
    # 2. Remove duplicates (safe no-op if there are none)
    # -----------------------------------------------------------------
    fear_greed = remove_duplicates(fear_greed, "Fear & Greed Index")
    trades = remove_duplicates(trades, "Historical Trader Data")

    # -----------------------------------------------------------------
    # 3. Convert timestamps to proper datetime / Date columns
    # -----------------------------------------------------------------
    # Fear & Greed: `date` column is already YYYY-MM-DD -> just parse it.
    fear_greed["Date"] = pd.to_datetime(fear_greed["date"], format="%Y-%m-%d")

    # Historical trades: `Timestamp IST` is DD-MM-YYYY HH:MM (human-readable,
    # IST timezone). We parse this (rather than the epoch-ms `Timestamp`
    # column) since it is unambiguous and already timezone-labelled.
    trades["datetime"] = pd.to_datetime(trades["Timestamp IST"], format="%d-%m-%Y %H:%M")

    # Reduce to daily granularity for merging with the daily sentiment index.
    trades["Date"] = trades["datetime"].dt.normalize()

    print("\n--- Post-conversion date ranges ---")
    print(f"Fear & Greed Date range:      {fear_greed['Date'].min()} -> {fear_greed['Date'].max()}")
    print(f"Historical trades Date range: {trades['Date'].min()} -> {trades['Date'].max()}")

    # -----------------------------------------------------------------
    # 4. Merge datasets on Date
    #    Left join: keep every trade row, attach that day's sentiment.
    #    (A small number of trading days may not have a sentiment label
    #    if the Fear/Greed index doesn't cover that date -> these will
    #    show up as NaN in `classification`/`value` after the merge.)
    # -----------------------------------------------------------------
    merged = trades.merge(
        fear_greed[["Date", "value", "classification"]],
        on="Date",
        how="left",
    )

    unmatched = merged["classification"].isnull().sum()
    print(f"\nTrade rows with no matching sentiment record: {unmatched}")

    print("\n--- Merged dataset preview ---")
    print(f"Shape: {merged.shape}")
    print(merged.head())

    # -----------------------------------------------------------------
    # 5. Save merged dataset
    # -----------------------------------------------------------------
    merged.to_csv(OUTPUT_PATH, index=False)
    print(f"\nMerged dataset saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
