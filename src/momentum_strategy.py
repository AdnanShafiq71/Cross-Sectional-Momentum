import pandas as pd

tickers = pd.read_csv("data/tickers.csv")

data = pd.read_csv("data/market_data.csv")

data["Date"] = pd.to_datetime(data["Date"])

data = data.sort_values(["Ticker", "Date"])

data["Close_1M_Ago"] = data.groupby("Ticker")["Close"].shift(21)

data["Close_12M_Ago"] = data.groupby("Ticker")["Close"].shift(252)

data["Momentum_12_1"] = (
    data["Close_1M_Ago"] / data["Close_12M_Ago"] - 1
)

data["Momentum_Rank"] = (
    data.groupby("Date")["Momentum_12_1"]
    .rank(ascending=False)
)

data["Month"] = data["Date"].dt.to_period("M")
month_end_dates = data.groupby("Month")["Date"].max()
month_end_data = data[data["Date"].isin(month_end_dates.values)]
month_end_data = month_end_data.dropna(subset=["Momentum_12_1"])

month_end_data["Position"] = 0

month_end_data.loc[
    month_end_data["Momentum_Rank"] <= 10,
    "Position"
] = 1

month_end_data.loc[
    month_end_data["Momentum_Rank"] >= 41,
    "Position"
] = -1

month_end_data["Holding_Month"] = (
    month_end_data["Month"] + 1
)

data["Daily_Return"] = (
    data.groupby("Ticker")["Close"].pct_change()
)

data = data.merge(
    month_end_data[["Ticker", "Holding_Month", "Position"]],
    left_on=["Ticker", "Month"],
    right_on=["Ticker", "Holding_Month"],
    how="left"
)

data["Strategy_Return"] = data["Daily_Return"] * data["Position"]

daily_portfolio_returns = (
    data[data["Position"].notna() & (data["Position"] != 0)]
    .groupby("Date")
    .apply(
        lambda x: pd.Series({
            "Long_Return": x.loc[x["Position"] == 1, "Daily_Return"].mean(),
            "Short_Return": x.loc[x["Position"] == -1, "Daily_Return"].mean()
        })
    )
    .reset_index()
)

daily_portfolio_returns["Long_Short_Return"] = (
    daily_portfolio_returns["Long_Return"]
    - daily_portfolio_returns["Short_Return"]
)

daily_portfolio_returns["Cumulative_Return"] = (
    1 + daily_portfolio_returns["Long_Short_Return"]
).cumprod()

total_return = (
    daily_portfolio_returns["Cumulative_Return"].iloc[-1] - 1
)


total_return = (
    daily_portfolio_returns["Cumulative_Return"].iloc[-1] - 1
)

years = (
    daily_portfolio_returns["Date"].max()
    - daily_portfolio_returns["Date"].min()
).days / 365.25

annualised_return = (
    daily_portfolio_returns["Cumulative_Return"].iloc[-1]
    ** (1 / years)
    - 1
)

annualised_volatility = (
    daily_portfolio_returns["Long_Short_Return"].std()
    * (252 ** 0.5)
)

sharpe_ratio = (
    annualised_return / annualised_volatility
)

running_peak = (
    daily_portfolio_returns["Cumulative_Return"].cummax()
)

drawdown = (
    daily_portfolio_returns["Cumulative_Return"]
    / running_peak
    - 1
)

maximum_drawdown = drawdown.min()

data.to_csv("data/strategy_data.csv", index=False)