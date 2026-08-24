import yfinance as yf

data = yf.download(
    "AAPL",
    start="2021-01-01",
    end="2026-01-01",
    auto_adjust=True
)

print(data.head())

data.columns = data.columns.get_level_values(0)

data = data.reset_index()

data["Ticker"] = "AAPL"

data = data[
    ["Date", "Ticker", "Open", "High", "Low", "Close", "Volume"]
]

data.to_csv("data/AAPL.csv", index=False)
print(data.head())