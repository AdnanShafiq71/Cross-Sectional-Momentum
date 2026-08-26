# Cross-Sectional Momentum Strategy — A Quantitative Research Project

A research project investigating whether a classic 12-1 cross-sectional
momentum strategy generates risk-adjusted returns in a fixed 50-stock
US large-cap equity universe, built with Python and SQL.

## Universe & Methodology

- **Universe:** a fixed set of 50 large-cap US equities (not the full S&P 500 —
  see Limitations below).
- **Signal:** 12-month price momentum, skipping the most recent month, ranked
  cross-sectionally each month.
- **Portfolio:** long the top N momentum stocks, short the bottom N,
  equal-weighted, rebalanced monthly.
- **Benchmark:** SPY (S&P 500 ETF), not an equal-weighted average of the
  universe itself.
- **Transaction costs:** modelled as a per-trade cost based on monthly turnover.

## Key Results (12-1, top/bottom 10, net of costs)

| Metric | Value |
|---|---|
| Total Return | [-10.1%] |
| Annualised Return | [-2.7%] |
| Annualised Volatility | [23.3%] |
| Sharpe Ratio (excess return) | [-0.17] |
| Sortino Ratio | [-0.23] |
| Max Drawdown | [-38.7%] |
| Calmar Ratio | [-0.07] |

## Statistical Significance

Newey-West t-statistic: [-0.000], p-value:  [0.999].
[One sentence: is the result statistically distinguishable from zero?]

## Parameter Research

Tested lookbacks of 3-1, 6-1, 9-1, 12-1, and 18-1 months, at both
top/bottom 5 and top/bottom 10 portfolio sizes, plus long-only variants.
Full results in `data/parameter_research.csv` and visualised in
`data/chart_parameter_heatmap.png`.
The best performing parameter was the long top 10 stocks only with an 18-1 month lookback period, achieving annual returns of 29.7% and a Sharpe ratio of 1.16.
The worst performing parameter was the long-short top and bottom 5 stocks with a 9-1 month lookback period, achieving annual returns of -11.6% and a Sharpe ratio of -0.354

## Long vs Short Leg Analysis

The long leg total return was 129.5% while the short leg total return was 122.4%. Both had roughly even levels of volatility at 23%/24%. This shows underperformance of the momentum strategy was driven by the short leg since it still achieved positive returns while our strategy was to short them.

## Transaction Cost Sensitivity

Tested cost assumptions of 0, 5, 10, 25, and 50 bps per trade.
See `data/cost_sensitivity.csv` and `data/chart_cost_sensitivity.png`.
The strategy is fragile in regards to transaction cost sensitivity. Our Sharpe ratio fell from -0.14 to -0.27 showing that there is a significant impact from trading costs.

## Charts

- `data/chart_equity_curve.png` — strategy vs S&P 500
- `data/chart_drawdown.png` — drawdown through time
- `data/chart_annual_returns.png` — yearly returns
- `data/chart_long_vs_short.png` — long vs short leg cumulative performance
- `data/chart_parameter_heatmap.png` — Sharpe by lookback x portfolio size
- `data/chart_cost_sensitivity.png` — Sharpe vs transaction cost level

## Project Structure

data/ Market data, results, charts
sql/ SQL analysis
src/ Python pipeline scripts

## Pipeline

```bash
python src/download_data.py        # download price + SPY data
python src/validate_data.py        # data quality checks
python src/momentum_strategy.py    # signal + raw backtest
python src/transaction_costs.py    # net-of-cost backtest
python src/performance_analysis.py # full report + core charts
python src/parameter_research.py   # lookback/size sweep
python src/parameter_heatmap.py    # heatmap chart
python src/cost_sensitivity.py     # cost sensitivity chart
python src/significance_test.py    # statistical significance
python src/build_database.py       # build SQLite DB
python src/run_sql_queries.py      # run SQL analysis
```

## Limitations

- **Survivorship bias:** the 50-stock universe was selected using
  currently-prominent large-cap names and tested backwards. Companies
  that were historically in a similarly-sized universe but later
  underperformed, were delisted, or acquired are not included. This
  likely biases results upward relative to a true point-in-time universe.
- **Universe size:** 50 stocks is a fixed sample, not the full S&P 500
  index — results should not be read as representative of the actual
  index constituents.
- **Risk-free rate:** approximated as a flat annual rate rather than a
  historical daily series.
- **Transaction cost model:** a simplified linear cost per unit of
  turnover; does not model market impact or bid-ask spread directly.

## What This Project Demonstrates

- End-to-end quant research pipeline: data → validation → signal →
  portfolio construction → cost modelling → performance analysis
- Robustness testing across signal parameters and cost assumptions
- Statistical rigor (Newey-West significance testing)
- Python + SQL integration (SQLite for querying and quality checks)
