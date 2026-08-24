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

print(
    data[data["Date"] == "2022-01-03"][
        ["Date", "Ticker", "Momentum_12_1", "Momentum_Rank"]
    ]
    .sort_values("Momentum_Rank")
)

data["Month"] = data["Date"].dt.to_period("M")
month_end_dates = data.groupby("Month")["Date"].max()
month_end_data = data[data["Date"].isin(month_end_dates.values)]
month_end_data = month_end_data.dropna(subset=["Momentum_12_1"])
print(month_end_data[["Date", "Ticker", "Momentum_12_1", "Momentum_Rank"]].head(20))

month_end_data["Position"] = 0

month_end_data.loc[
    month_end_data["Momentum_Rank"] <= 10,
    "Position"
] = 1

month_end_data.loc[
    month_end_data["Momentum_Rank"] >= 41,
    "Position"
] = -1
print(
    month_end_data[
        ["Date", "Ticker", "Momentum_Rank", "Position"]
    ].head(50)
)