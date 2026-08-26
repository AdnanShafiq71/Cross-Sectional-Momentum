import pandas as pd
import numpy as np

market_data = pd.read_csv("data/market_data.csv")
market_data["Date"] = pd.to_datetime(market_data["Date"])
market_data = market_data.sort_values(["Ticker", "Date"])
market_data["Daily_Return"] = market_data.groupby("Ticker")["Close"].pct_change()


def run_backtest(lookback_months, n_positions, long_only=False, skip_months=1):
    """
    Runs one momentum backtest for a given lookback period and portfolio size.
    Returns a dict of performance metrics. Uses RAW returns (no transaction
    costs yet - that comes in Phase 3).
    """
    data = market_data.copy()

    skip_days = skip_months * 21
    lookback_days = lookback_months * 21

    data["Close_Skip_Ago"] = data.groupby("Ticker")["Close"].shift(skip_days)
    data["Close_Lookback_Ago"] = data.groupby("Ticker")["Close"].shift(lookback_days)

    data["Momentum"] = data["Close_Skip_Ago"] / data["Close_Lookback_Ago"] - 1
    data["Momentum_Rank"] = data.groupby("Date")["Momentum"].rank(ascending=False)

    data["Month"] = data["Date"].dt.to_period("M")
    month_end_dates = data.groupby("Month")["Date"].max()
    month_end_data = data[data["Date"].isin(month_end_dates.values)]
    month_end_data = month_end_data.dropna(subset=["Momentum"]).copy()

    n_stocks = data["Ticker"].nunique()

    month_end_data["Position"] = 0
    month_end_data.loc[month_end_data["Momentum_Rank"] <= n_positions, "Position"] = 1

    if not long_only:
        month_end_data.loc[
            month_end_data["Momentum_Rank"] > n_stocks - n_positions, "Position"
        ] = -1

    month_end_data["Holding_Month"] = month_end_data["Month"] + 1

    data = data.merge(
        month_end_data[["Ticker", "Holding_Month", "Position"]],
        left_on=["Ticker", "Month"],
        right_on=["Ticker", "Holding_Month"],
        how="left"
    )

    positioned = data[data["Position"].notna() & (data["Position"] != 0)]

    daily = (
        positioned.groupby("Date")
        .apply(lambda x: pd.Series({
            "Long_Return": x.loc[x["Position"] == 1, "Daily_Return"].mean(),
            "Short_Return": (
                x.loc[x["Position"] == -1, "Daily_Return"].mean()
                if not long_only else np.nan
            )
        }))
        .reset_index()
    )

    daily["Strategy_Return"] = (
        daily["Long_Return"] if long_only
        else daily["Long_Return"] - daily["Short_Return"]
    )
    daily = daily.dropna(subset=["Strategy_Return"])
    daily["Cumulative_Return"] = (1 + daily["Strategy_Return"]).cumprod()

    years = (daily["Date"].max() - daily["Date"].min()).days / 365.25
    total_return = daily["Cumulative_Return"].iloc[-1] - 1
    annual_return = (1 + total_return) ** (1 / years) - 1
    annual_vol = daily["Strategy_Return"].std() * (252 ** 0.5)

    risk_free_daily = 1.04 ** (1 / 252) - 1
    excess = daily["Strategy_Return"] - risk_free_daily
    sharpe = excess.mean() / excess.std() * (252 ** 0.5)

    running_max = daily["Cumulative_Return"].cummax()
    drawdown = daily["Cumulative_Return"] / running_max - 1
    max_dd = drawdown.min()

    return {
        "Annual_Return": annual_return,
        "Volatility": annual_vol,
        "Sharpe": sharpe,
        "Max_Drawdown": max_dd
    }


lookbacks = [3, 6, 9, 12, 18]
portfolio_sizes = [5, 10]

results = []

for lb in lookbacks:
    for size in portfolio_sizes:
        metrics = run_backtest(lookback_months=lb, n_positions=size, long_only=False)
        metrics.update({"Lookback": f"{lb}-1", "Portfolio": f"{size}/{size}", "Type": "Long-Short"})
        results.append(metrics)

    lo_metrics = run_backtest(lookback_months=lb, n_positions=10, long_only=True)
    lo_metrics.update({"Lookback": f"{lb}-1", "Portfolio": "10 Long Only", "Type": "Long-Only"})
    results.append(lo_metrics)

results_df = pd.DataFrame(results)[
    ["Lookback", "Portfolio", "Type", "Annual_Return", "Volatility", "Sharpe", "Max_Drawdown"]
]
results_df = results_df.sort_values("Sharpe", ascending=False)

results_df.to_csv("data/parameter_research.csv", index=False)
print(results_df.to_string(index=False))