import pandas as pd


tickers = pd.read_csv("data/tickers.csv")
data = pd.read_csv("data/market_data.csv")

data["Date"] = pd.to_datetime(data["Date"])


print("========== DATASET OVERVIEW ==========")

print("Number of rows:", len(data))
print("Number of stocks:", data["Ticker"].nunique())

print("\nDate range:")
print(data["Date"].min(), "to", data["Date"].max())


print("\n========== MISSING VALUES ==========")

print(data.isnull().sum())


print("\n========== DUPLICATES ==========")

print(
    "Duplicate rows:",
    data.duplicated().sum()
)

print(
    "Duplicate Date-Ticker combinations:",
    data.duplicated(
        subset=["Date", "Ticker"]
    ).sum()
)


print("\n========== TICKER CHECK ==========")

expected_tickers = set(tickers["Ticker"])
actual_tickers = set(data["Ticker"])

missing_tickers = expected_tickers - actual_tickers
unexpected_tickers = actual_tickers - expected_tickers

print("Missing tickers:", missing_tickers)
print("Unexpected tickers:", unexpected_tickers)


print("\n========== PRICE CHECK ==========")

price_columns = [
    "Open",
    "High",
    "Low",
    "Close"
]

for column in price_columns:

    negative_values = (
        data[column] <= 0
    ).sum()

    print(
        f"{column} <= 0:",
        negative_values
    )


print("\n========== VOLUME CHECK ==========")

print(
    "Negative volume:",
    (data["Volume"] < 0).sum()
)


print("\n========== DATE ORDER CHECK ==========")

data = data.sort_values(
    ["Ticker", "Date"]
)

duplicate_dates = (
    data.groupby("Ticker")["Date"]
    .apply(lambda x: x.duplicated().sum())
    .sum()
)

print(
    "Duplicate dates within ticker:",
    duplicate_dates
)


print("\n========== DATA VALIDATION COMPLETE ==========")