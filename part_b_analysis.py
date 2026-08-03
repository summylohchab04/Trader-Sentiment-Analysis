"""
Part B — Analysis
Trader Performance vs Market Sentiment (Hyperliquid)

Reads merged_data.csv (produced in Part A) and:
1. Compares trader performance on Fear vs Greed days
   (Total PnL, Average PnL, Win Rate, Drawdown proxy).
2. Analyzes behavioral changes by sentiment
   (trade frequency, leverage proxy, trade size, long/short ratio).
3. Segments traders into High/Low leverage, Frequent/Infrequent,
   and Consistent/Inconsistent winners.
4. Saves 7 professional PNG charts into a "charts" folder.
5. Prints summary tables for every analysis.

No written insights/report are produced here — that is Part C.

Run with: python part_b_analysis.py
Expects merged_data.csv in the same folder (update MERGED_DATA_PATH if needed).
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 0. CONFIG
# ---------------------------------------------------------------------------
MERGED_DATA_PATH = "merged_data.csv"
CHARTS_DIR = "charts"

# Consistent color palette / order for sentiment classifications
SENTIMENT_ORDER = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]
SENTIMENT_COLORS = {
    "Extreme Fear": "#8B0000",
    "Fear": "#E74C3C",
    "Neutral": "#95A5A6",
    "Greed": "#2ECC71",
    "Extreme Greed": "#145A32",
}

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

plt.rcParams.update({
    "figure.figsize": (9, 5.5),
    "figure.dpi": 120,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "font.size": 11,
})


def ordered_categories(present_values):
    """Return SENTIMENT_ORDER filtered down to values actually present."""
    return [s for s in SENTIMENT_ORDER if s in present_values]


def save_bar_chart(series, title, ylabel, filename, colors=None, fmt="{:.2f}"):
    """Helper to draw & save a clean single-series bar chart."""
    fig, ax = plt.subplots()
    bars = ax.bar(
        series.index.astype(str),
        series.values,
        color=[colors[c] for c in series.index] if colors else "#3B82C4",
        edgecolor="black",
        linewidth=0.5,
    )
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.axhline(0, color="black", linewidth=0.8)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            fmt.format(height),
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4 if height >= 0 else -12),
            textcoords="offset points",
            ha="center",
            fontsize=9,
        )
    plt.xticks(rotation=15)
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, filename))
    plt.close(fig)
    print(f"  Saved chart: {CHARTS_DIR}/{filename}")


def main():
    os.makedirs(CHARTS_DIR, exist_ok=True)

    # -----------------------------------------------------------------
    # 1. Load merged data
    # -----------------------------------------------------------------
    df = pd.read_csv(MERGED_DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"])

    # Drop the handful of trade rows with no matching sentiment record
    # (identified in Part A) since they cannot be used in sentiment analysis.
    before = len(df)
    df = df.dropna(subset=["classification"]).copy()
    print(f"Dropped {before - len(df)} row(s) with no sentiment match. Remaining rows: {len(df)}")

    # Restrict chart/category ordering to classifications actually present
    cats_present = ordered_categories(df["classification"].unique())
    df["classification"] = pd.Categorical(df["classification"], categories=cats_present, ordered=True)

    # A simplified binary sentiment grouping used for headline Fear vs Greed
    # comparisons (Neutral days are excluded from this specific binary view,
    # but remain included in the 5-category breakdowns).
    sentiment_map = {
        "Extreme Fear": "Fear",
        "Fear": "Fear",
        "Neutral": "Neutral",
        "Greed": "Greed",
        "Extreme Greed": "Greed",
    }
    df["sentiment_group"] = df["classification"].map(sentiment_map)

    # -----------------------------------------------------------------
    # 2. Feature engineering
    # -----------------------------------------------------------------
    # A trade is treated as "closing" (realizing PnL) if Closed PnL != 0.
    df["is_closing_trade"] = df["Closed PnL"] != 0
    df["is_win"] = df["Closed PnL"] > 0

    # Leverage proxy:
    # This dataset does NOT contain a native margin/leverage column.
    # We construct a bounded proxy in [0, 1]:
    #   leverage_proxy = Size USD / (existing_position_notional + Size USD)
    # where existing_position_notional = |Start Position| * Execution Price.
    # A value near 1 means this single trade drives most of the resulting
    # notional exposure (aggressive/high relative risk-taking); a value
    # near 0 means the trade is small relative to an already large position.
    existing_notional = df["Start Position"].abs() * df["Execution Price"]
    resulting_notional = existing_notional + df["Size USD"]
    df["leverage_proxy"] = df["Size USD"] / resulting_notional.replace(0, np.nan)
    df["leverage_proxy"] = df["leverage_proxy"].fillna(0)

    # -----------------------------------------------------------------
    # 3. TASK 1 — Performance: Fear vs Greed
    # -----------------------------------------------------------------
    print("\n" + "=" * 70)
    print("TASK 1: PERFORMANCE — FEAR vs GREED")
    print("=" * 70)

    # 1a. Total & average Closed PnL, and win rate, by classification
    perf_by_class = df.groupby("classification", observed=True).agg(
        total_closed_pnl=("Closed PnL", "sum"),
        avg_closed_pnl=("Closed PnL", "mean"),
        n_trades=("Closed PnL", "size"),
    )
    closing_trades = df[df["is_closing_trade"]]
    win_rate_by_class = closing_trades.groupby("classification", observed=True)["is_win"].mean() * 100
    perf_by_class["win_rate_pct"] = win_rate_by_class
    print("\n--- Performance by sentiment classification ---")
    print(perf_by_class)

    # 1b. Same metrics using the simplified binary Fear vs Greed grouping
    binary_df = df[df["sentiment_group"].isin(["Fear", "Greed"])]
    perf_by_group = binary_df.groupby("sentiment_group", observed=True).agg(
        total_closed_pnl=("Closed PnL", "sum"),
        avg_closed_pnl=("Closed PnL", "mean"),
        n_trades=("Closed PnL", "size"),
    )
    binary_closing = binary_df[binary_df["is_closing_trade"]]
    perf_by_group["win_rate_pct"] = binary_closing.groupby("sentiment_group", observed=True)["is_win"].mean() * 100
    print("\n--- Performance: Fear vs Greed (binary grouping) ---")
    print(perf_by_group)

    # 1c. Drawdown proxy — daily cumulative PnL across all traders
    daily_pnl = df.groupby("Date", observed=True).agg(
        daily_pnl=("Closed PnL", "sum"),
    ).reset_index()
    daily_pnl = daily_pnl.sort_values("Date")
    daily_pnl["cumulative_pnl"] = daily_pnl["daily_pnl"].cumsum()
    daily_pnl["running_max"] = daily_pnl["cumulative_pnl"].cummax()
    daily_pnl["drawdown"] = daily_pnl["cumulative_pnl"] - daily_pnl["running_max"]

    # Attach each day's sentiment classification (mode, since a day is one row anyway)
    day_sentiment = df.groupby("Date", observed=True)["classification"].first()
    daily_pnl = daily_pnl.merge(day_sentiment.rename("classification"), on="Date", how="left")

    drawdown_by_class = daily_pnl.groupby("classification", observed=True)["drawdown"].mean()
    print("\n--- Average daily drawdown proxy by sentiment classification ---")
    print(drawdown_by_class)
    print(f"\nMax cumulative drawdown observed: {daily_pnl['drawdown'].min():,.2f}")

    # -----------------------------------------------------------------
    # 4. TASK 2 — Behavior: trade frequency, leverage, size, long/short
    # -----------------------------------------------------------------
    print("\n" + "=" * 70)
    print("TASK 2: BEHAVIOR vs SENTIMENT")
    print("=" * 70)

    # 2a. Number of trades per day, averaged by sentiment
    trades_per_day = df.groupby(["Date", "classification"], observed=True).size().reset_index(name="n_trades")
    freq_by_class = trades_per_day.groupby("classification", observed=True)["n_trades"].mean()
    print("\n--- Average number of trades per day, by sentiment ---")
    print(freq_by_class)

    # 2b. Average leverage proxy by sentiment
    leverage_by_class = df.groupby("classification", observed=True)["leverage_proxy"].mean()
    print("\n--- Average leverage proxy by sentiment ---")
    print(leverage_by_class)

    # 2c. Average trade size (USD) by sentiment
    size_by_class = df.groupby("classification", observed=True)["Size USD"].mean()
    print("\n--- Average trade size (USD) by sentiment ---")
    print(size_by_class)

    # 2d. Long vs Short ratio by sentiment (based on Side: BUY = long-ish, SELL = short-ish)
    side_counts = df.groupby(["classification", "Side"], observed=True).size().unstack(fill_value=0)
    side_counts["long_short_ratio"] = side_counts.get("BUY", 0) / side_counts.get("SELL", 1).replace(0, np.nan)
    print("\n--- BUY/SELL counts and Long/Short ratio by sentiment ---")
    print(side_counts)

    # -----------------------------------------------------------------
    # 5. TASK 3 — Trader segmentation
    # -----------------------------------------------------------------
    print("\n" + "=" * 70)
    print("TASK 3: TRADER SEGMENTATION")
    print("=" * 70)

    # Aggregate per-account stats first
    account_stats = df.groupby("Account").agg(
        total_trades=("Closed PnL", "size"),
        avg_leverage=("leverage_proxy", "mean"),
        total_pnl=("Closed PnL", "sum"),
        avg_pnl=("Closed PnL", "mean"),
    )
    acct_closing = df[df["is_closing_trade"]].groupby("Account")["is_win"].mean() * 100
    account_stats["win_rate_pct"] = acct_closing
    account_stats["win_rate_pct"] = account_stats["win_rate_pct"].fillna(0)

    # 3a. High vs Low leverage (split at median avg_leverage)
    lev_median = account_stats["avg_leverage"].median()
    account_stats["leverage_segment"] = np.where(
        account_stats["avg_leverage"] >= lev_median, "High Leverage", "Low Leverage"
    )

    # 3b. Frequent vs Infrequent traders (split at median total_trades)
    trades_median = account_stats["total_trades"].median()
    account_stats["frequency_segment"] = np.where(
        account_stats["total_trades"] >= trades_median, "Frequent", "Infrequent"
    )

    # 3c. Consistent winners vs Inconsistent (split at median win_rate_pct)
    winrate_median = account_stats["win_rate_pct"].median()
    account_stats["consistency_segment"] = np.where(
        account_stats["win_rate_pct"] >= winrate_median, "Consistent Winner", "Inconsistent"
    )

    print(f"\nMedian avg leverage proxy across accounts: {lev_median:.4f}")
    print(f"Median total trades across accounts: {trades_median:.1f}")
    print(f"Median win rate (%) across accounts: {winrate_median:.2f}")

    print("\n--- Account-level segment summary ---")
    print(account_stats)

    # Segment-level comparison tables (avg PnL & avg win rate per segment)
    leverage_seg_summary = account_stats.groupby("leverage_segment").agg(
        avg_total_pnl=("total_pnl", "mean"),
        avg_win_rate=("win_rate_pct", "mean"),
        n_accounts=("total_trades", "size"),
    )
    frequency_seg_summary = account_stats.groupby("frequency_segment").agg(
        avg_total_pnl=("total_pnl", "mean"),
        avg_win_rate=("win_rate_pct", "mean"),
        n_accounts=("total_trades", "size"),
    )
    consistency_seg_summary = account_stats.groupby("consistency_segment").agg(
        avg_total_pnl=("total_pnl", "mean"),
        avg_win_rate=("win_rate_pct", "mean"),
        n_accounts=("total_trades", "size"),
    )

    print("\n--- Segment comparison: High vs Low Leverage ---")
    print(leverage_seg_summary)
    print("\n--- Segment comparison: Frequent vs Infrequent ---")
    print(frequency_seg_summary)
    print("\n--- Segment comparison: Consistent Winner vs Inconsistent ---")
    print(consistency_seg_summary)

    # -----------------------------------------------------------------
    # 6. CHARTS
    # -----------------------------------------------------------------
    print("\n" + "=" * 70)
    print("GENERATING CHARTS")
    print("=" * 70)

    # Chart 1: Total PnL by sentiment
    save_bar_chart(
        perf_by_class["total_closed_pnl"],
        "Total Closed PnL by Market Sentiment",
        "Total Closed PnL (USD)",
        "01_pnl_by_sentiment.png",
        colors=SENTIMENT_COLORS,
        fmt="{:,.0f}",
    )

    # Chart 2: Win rate by sentiment
    save_bar_chart(
        perf_by_class["win_rate_pct"],
        "Win Rate (%) by Market Sentiment",
        "Win Rate (%)",
        "02_win_rate_by_sentiment.png",
        colors=SENTIMENT_COLORS,
        fmt="{:.1f}%",
    )

    # Chart 3: Trade frequency by sentiment
    save_bar_chart(
        freq_by_class,
        "Average Trades per Day by Market Sentiment",
        "Avg. Trades / Day",
        "03_trade_frequency_by_sentiment.png",
        colors=SENTIMENT_COLORS,
        fmt="{:.1f}",
    )

    # Chart 4: Average leverage proxy by sentiment
    save_bar_chart(
        leverage_by_class,
        "Average Leverage Proxy by Market Sentiment",
        "Avg. Leverage Proxy (0-1 scale)",
        "04_avg_leverage_by_sentiment.png",
        colors=SENTIMENT_COLORS,
        fmt="{:.3f}",
    )

    # Chart 5: Average trade size (USD) by sentiment
    save_bar_chart(
        size_by_class,
        "Average Trade Size (USD) by Market Sentiment",
        "Avg. Trade Size (USD)",
        "05_avg_trade_size_by_sentiment.png",
        colors=SENTIMENT_COLORS,
        fmt="{:,.0f}",
    )

    # Chart 6: Long vs Short ratio by sentiment
    save_bar_chart(
        side_counts["long_short_ratio"],
        "Long/Short Ratio (BUY:SELL) by Market Sentiment",
        "Long/Short Ratio",
        "06_long_short_ratio_by_sentiment.png",
        colors=SENTIMENT_COLORS,
        fmt="{:.2f}",
    )

    # Chart 7: Trader segment comparison (3-panel: leverage / frequency / consistency)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    segment_tables = [
        (leverage_seg_summary, "High vs Low Leverage", axes[0]),
        (frequency_seg_summary, "Frequent vs Infrequent", axes[1]),
        (consistency_seg_summary, "Consistent vs Inconsistent", axes[2]),
    ]
    for table, subtitle, ax in segment_tables:
        x = np.arange(len(table.index))
        width = 0.35
        ax2 = ax.twinx()
        bars1 = ax.bar(x - width / 2, table["avg_total_pnl"], width, label="Avg Total PnL (USD)", color="#3B82C4")
        bars2 = ax2.bar(x + width / 2, table["avg_win_rate"], width, label="Avg Win Rate (%)", color="#F5A623")
        ax.set_xticks(x)
        ax.set_xticklabels(table.index, rotation=10)
        ax.set_title(subtitle, fontsize=11, fontweight="bold")
        ax.set_ylabel("Avg Total PnL (USD)")
        ax2.set_ylabel("Avg Win Rate (%)")
        ax.axhline(0, color="black", linewidth=0.6)
        lines_labels = [ax.get_legend_handles_labels(), ax2.get_legend_handles_labels()]
        lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
        ax.legend(lines, labels, loc="upper right", fontsize=8)
    fig.suptitle("Trader Segment Comparison", fontsize=14, fontweight="bold")
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, "07_trader_segment_comparison.png"))
    plt.close(fig)
    print(f"  Saved chart: {CHARTS_DIR}/07_trader_segment_comparison.png")

    # Bonus supporting chart: cumulative PnL / drawdown curve over time
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(daily_pnl["Date"], daily_pnl["cumulative_pnl"], color="#2E86C1", linewidth=1.5, label="Cumulative PnL")
    ax.plot(daily_pnl["Date"], daily_pnl["running_max"], color="grey", linestyle="--", linewidth=1, label="Running Peak")
    ax.fill_between(
        daily_pnl["Date"], daily_pnl["cumulative_pnl"], daily_pnl["running_max"],
        color="red", alpha=0.2, label="Drawdown"
    )
    ax.set_title("Cumulative PnL & Drawdown Proxy Over Time", fontsize=13, fontweight="bold")
    ax.set_ylabel("PnL (USD)")
    ax.legend(loc="upper left", fontsize=9)
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, "08_cumulative_pnl_drawdown.png"))
    plt.close(fig)
    print(f"  Saved chart: {CHARTS_DIR}/08_cumulative_pnl_drawdown.png")

    print("\nAll charts saved to the 'charts' folder.")


if __name__ == "__main__":
    main()
