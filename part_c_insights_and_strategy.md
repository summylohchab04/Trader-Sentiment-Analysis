# Part C — Insights & Strategy Recommendations
### Trader Performance vs. Market Sentiment (Hyperliquid)

---

## 1. Key Insights

### Insight 1: Fear days deliver more resilient risk-adjusted performance despite lower average trade size

Total closed PnL was highest on **Fear** days (**$3.36M**) and **Extreme Greed** days (**$2.72M**), while **Extreme Fear** days produced the lowest total PnL (**$739K**) despite the highest trade frequency (see *01_pnl_by_sentiment.png* and *03_trade_frequency_by_sentiment.png*). More tellingly, the **average daily drawdown proxy** (*08_cumulative_pnl_drawdown.png*) was deepest on **Fear** (–$38.1K/day) and **Extreme Fear** (–$36.6K/day) days and shallowest on **Extreme Greed** days (–$2.7K/day). This indicates that while traders are net profitable across all sentiment regimes, capital swings and drawdown risk are materially larger during Fear regimes than Greed regimes — profitability during Fear is coming with a rougher equity curve, not a smoother one.

### Insight 2: Traders scale up leverage and position aggressiveness as sentiment shifts from Fear to Greed, even though win rate does not improve monotonically

The average leverage proxy rose steadily and monotonically from **Extreme Fear (0.066)** → **Fear (0.067)** → **Neutral (0.087)** → **Greed (0.106)** → **Extreme Greed (0.130)** (*04_avg_leverage_by_sentiment.png*). However, win rate did **not** follow the same clean trend — it was highest in **Extreme Greed (89.2%)** and **Fear (87.3%)**, but dipped in **Greed (76.9%)** and **Extreme Fear (76.2%)** (*02_win_rate_by_sentiment.png*). This mismatch suggests that rising leverage in Greed regimes is not simply "riding a winning streak" — traders are taking on more relative exposure per trade in Greed conditions without a corresponding, consistent improvement in hit rate.

### Insight 3: Extreme Fear days are dominated by high trade frequency rather than trade size, and show a short-selling skew unique to Extreme Greed

Trade frequency was over **2x–6x** higher on Extreme Fear days (**1,529 trades/day** on average) compared to every other regime, particularly Greed (**261 trades/day**) (*03_trade_frequency_by_sentiment.png*), while average trade size actually stayed moderate ($5,350) rather than spiking. Separately, the long/short ratio (BUY:SELL) was roughly balanced across Extreme Fear, Fear, Neutral, and Greed (0.96–1.04), but dropped sharply to **0.81** in Extreme Greed (*06_long_short_ratio_by_sentiment.png*) — i.e., traders sold more than they bought during the most euphoric sentiment days, consistent with profit-taking/de-risking behavior into strength rather than chasing the rally.

At the trader-segmentation level (*07_trader_segment_comparison.png*), **Low Leverage** accounts outperformed **High Leverage** accounts on both average total PnL ($373.5K vs. $267.4K) and win rate (82.2% vs. 87.8% — note win rate is higher for High Leverage, but PnL is lower, reinforcing Insight 2's point that higher relative exposure doesn't translate into proportionally higher account-level PnL). **Frequent traders** generated far higher average total PnL ($496.5K) than **Infrequent traders** ($144.4K), but with a lower win rate (83.3% vs. 86.7%) — consistent with a higher-volume, lower-hit-rate style. **Consistent Winners** (win rate ≥ median) had a lower average total PnL ($281.9K) than **Inconsistent** traders ($359.0K), suggesting that a small number of high-conviction/high-size wins from lower-win-rate traders can outweigh a high hit rate from smaller, more conservative traders.

---

## 2. Strategy Recommendations

### Recommendation 1: Cap effective exposure for high-frequency traders specifically during Extreme Fear regimes

- **Target segment:** Frequent traders (trade count ≥ account median)
- **Applicable sentiment:** Extreme Fear
- **Recommended action:** Impose a soft daily exposure/trade-count cap (or a tiered leverage step-down) for frequent traders specifically on Extreme Fear days, rather than restricting all traders equally.
- **Reasoning:** Extreme Fear days show the highest trade frequency of any regime (1,529 trades/day) combined with the lowest total PnL ($739K) and among the deepest average drawdowns (–$36.6K/day). Frequent traders as a segment already carry a lower win rate (83.3%) than infrequent traders (86.7%), so concentrating more trades into the regime with the weakest realized outcomes compounds the risk rather than diversifying it.
- **Expected benefit:** Reducing over-trading during the regime with the worst realized PnL-to-drawdown trade-off should improve risk-adjusted returns for the frequent-trader segment without meaningfully reducing their profitable Greed-day activity.

### Recommendation 2: Tighten leverage limits for the High Leverage segment as sentiment moves into Greed/Extreme Greed

- **Target segment:** High Leverage traders (leverage proxy ≥ account median)
- **Applicable sentiment:** Greed and Extreme Greed
- **Recommended action:** Introduce a leverage ceiling (or margin buffer requirement) that scales down as the sentiment index moves further into Greed, rather than allowing leverage to keep climbing with sentiment (as currently observed).
- **Reasoning:** Average leverage proxy rises monotonically from Fear (0.067) to Extreme Greed (0.130), but win rate does not rise in step (dipping to 76.9% in Greed) and, at the segment level, High Leverage accounts show *lower* average total PnL ($267.4K) than Low Leverage accounts ($373.5K) despite a higher win rate. This pattern — more leverage, inconsistent hit-rate improvement, and lower average PnL — points to leverage in Greed regimes amplifying variance rather than reliably amplifying edge.
- **Expected benefit:** Constraining leverage growth specifically in Greed/Extreme Greed should reduce the likelihood of large drawdowns from over-levered positions in a regime where historical PnL-per-unit-of-leverage has been comparatively weaker, protecting capital heading into any subsequent sentiment reversal.

---

## 3. Assumptions & Limitations

- **Leverage proxy, not true leverage:** The merged dataset does not contain a native margin/leverage column. Leverage was estimated using a derived proxy — `Size USD / (existing position notional + Size USD)`, bounded between 0 and 1 — which reflects how much of a trade's *resulting* notional exposure is driven by the current order, not the trader's actual margin-to-equity ratio. Absolute leverage figures (e.g., "0.13") should therefore be read as a *relative* risk-taking indicator, not as an actual leverage multiple (e.g., 5x, 10x).
- **Six unmatched trade rows:** Six rows in `merged_data.csv` had no corresponding Fear/Greed sentiment record for their trade date and were excluded from all sentiment-based analysis in Part B (211,224 → 211,218 rows analyzed). This is a negligible fraction of the dataset (<0.01%) and is not expected to materially affect the conclusions.
- **Closed PnL reflects realized profit only:** `Closed PnL` only captures profit/loss on trades that closed a position; a large share of rows (roughly half, per Part A inspection) have `Closed PnL = 0` because they represent position-opening or partial-fill trades. Unrealized PnL on open positions is not captured anywhere in this dataset, so total/average PnL figures understate a trader's true mark-to-market performance at any given point in time.
- **Win rate is computed on closing trades only:** Win rate = % of trades with `Closed PnL > 0`, calculated only among trades where `Closed PnL != 0`. Trades that open or add to a position (with `Closed PnL = 0`) are excluded from the win-rate denominator, which is standard practice but means win rate is not simply "% of all trade rows."
- **Sentiment classification is a daily-level label, trades are intraday:** The Fear/Greed index provides one classification per calendar day, which is applied uniformly to every trade executed that day. Any intraday sentiment shifts (e.g., a day starting as Fear and ending as Greed) are not captured — all trades on a given date inherit a single daily label.
- **Account-level segmentation uses a single historical median split:** High/Low Leverage, Frequent/Infrequent, and Consistent/Inconsistent segments were defined using the median value across all 32 accounts over the *entire* dataset period (May 2023 – May 2025), not a rolling or sentiment-specific median. Trader behavior/segment membership is therefore treated as static across the whole period, even though individual traders may have shifted style over time.
- **Small account universe:** The dataset contains only 32 unique trader accounts. Segment comparisons (16 accounts per segment) are directionally informative but represent a small sample; individual outlier accounts (e.g., very high trade-count or very large single-day PnL swings) can meaningfully shift segment averages.
- **`Coin` field uses non-standard tickers:** Instruments are labeled like `@107`, `@1`, etc. (246 unique values) rather than conventional symbols (BTC, ETH), consistent with Hyperliquid's internal index/perp naming. No asset-level breakdown was performed in this analysis; all results are aggregated across instruments.
