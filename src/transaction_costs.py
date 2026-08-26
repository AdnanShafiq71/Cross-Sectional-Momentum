import pandas as pd

data = pd.read_csv("data/strategy_data.csv")

data["Date"] = pd.to_datetime(data["Date"])

data["Month"] = data["Date"].dt.to_period("M")

monthly_positions = (
    data[data["Momentum_Rank"].notna()]
    .sort_values(["Ticker", "Date"])
    .groupby(["Ticker", "Month"])["Position"]
    .last()
    .reset_index()
)

monthly_positions["Previous_Position"] = (
    monthly_positions
    .groupby("Ticker")["Position"]
    .shift(1)
)

monthly_positions["Position_Change"] = (
    monthly_positions["Position"]
    - monthly_positions["Previous_Position"]
)

monthly_positions["Turnover"] = (
    monthly_positions["Position_Change"].abs() / 10
)

monthly_turnover = (
    monthly_positions
    .groupby("Month")["Turnover"]
    .sum()
    / 2
).reset_index()

transaction_cost_rate = 0.001

monthly_turnover["Transaction_Cost"] = (
    monthly_turnover["Turnover"]
    * transaction_cost_rate
)

monthly_turnover.to_csv(
    "data/monthly_turnover.csv",
    index=False
)

daily_returns = (
    data[
        data["Position"].notna()
        & (data["Position"] != 0)
    ]
    .groupby("Date")
    .apply(
        lambda x: pd.Series({
            "Long_Return": x.loc[
                x["Position"] == 1, "Daily_Return"
            ].mean(),
            "Short_Return": x.loc[
                x["Position"] == -1, "Daily_Return"
            ].mean()
        })
    )
    .reset_index()
)

daily_returns["Long_Short_Return"] = (
    daily_returns["Long_Return"]
    - daily_returns["Short_Return"]
)

daily_returns["Month"] = (
    pd.to_datetime(daily_returns["Date"]).dt.to_period("M")
)

daily_returns = daily_returns.merge(
    monthly_turnover[["Month", "Transaction_Cost"]],
    on="Month",
    how="left"
)

daily_returns["Transaction_Cost"] = (
    daily_returns["Transaction_Cost"]
    .where(
        daily_returns["Month"] != daily_returns["Month"].shift(1),
        0
    )
)

daily_returns["Net_Return"] = (
    daily_returns["Long_Short_Return"]
    - daily_returns["Transaction_Cost"]
)

daily_returns["Cumulative_Return"] = (
    1 + daily_returns["Net_Return"]
).cumprod()

total_return = (
    daily_returns["Cumulative_Return"].iloc[-1] - 1
)

backtest_years = (
    (daily_returns["Date"].iloc[-1]
     - daily_returns["Date"].iloc[0]).days / 365.25
)

annualised_return = (
    (1 + total_return) ** (1 / backtest_years) - 1
)

annualised_volatility = (
    daily_returns["Net_Return"].std() * (252 ** 0.5)
)

risk_free_rate_annual = 0.04  # approx. average T-bill rate
risk_free_rate_daily = (1 + risk_free_rate_annual) ** (1 / 252) - 1

excess_returns = daily_returns["Net_Return"] - risk_free_rate_daily

sharpe_ratio = (
    excess_returns.mean() / excess_returns.std() * (252 ** 0.5)
)

running_max = (
    daily_returns["Cumulative_Return"].cummax()
)

drawdown = (
    daily_returns["Cumulative_Return"] / running_max - 1
)

maximum_drawdown = drawdown.min()

daily_returns.to_csv(
    "data/backtest_results.csv",
    index=False
)