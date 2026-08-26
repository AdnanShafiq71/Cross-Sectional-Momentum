import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("data/backtest_results.csv")
market_data = pd.read_csv("data/market_data.csv")

data["Date"] = pd.to_datetime(data["Date"])
market_data["Date"] = pd.to_datetime(market_data["Date"])

plt.figure(figsize=(10, 6))

plt.plot(
    data["Date"],
    data["Cumulative_Return"]
)

plt.title("Cross-Sectional Momentum Strategy")
plt.xlabel("Date")
plt.ylabel("Cumulative Return")
plt.grid(True)

plt.show()

spy = pd.read_csv("data/spy_data.csv")
spy["Date"] = pd.to_datetime(spy["Date"])
spy = spy.sort_values("Date")

spy["Benchmark_Return"] = spy["SPY_Close"].pct_change()

spy = spy[spy["Date"] >= data["Date"].min()].copy()

spy["Benchmark_Cumulative"] = (
    1 + spy["Benchmark_Return"]
).cumprod()

benchmark = spy


plt.figure(figsize=(10, 6))

plt.plot(
    data["Date"],
    data["Cumulative_Return"],
    label="Momentum Strategy"
)

plt.plot(
    benchmark["Date"],
    benchmark["Benchmark_Cumulative"],
    label="S&P 500 (SPY)"
)

plt.title("Momentum Strategy vs S&P 500 (SPY)")
plt.xlabel("Date")
plt.ylabel("Growth of £1")
plt.legend()
plt.grid(True)

plt.show()

position_counts = (
    pd.read_csv("data/strategy_data.csv")
    .groupby(["Date", "Position"])
    .size()
    .unstack(fill_value=0)
)

strategy_data = pd.read_csv("data/strategy_data.csv")

strategy_data["Date"] = pd.to_datetime(strategy_data["Date"])

daily_long_short = (
    strategy_data[strategy_data["Position"].isin([-1, 1])]
    .groupby(["Date", "Position"])["Daily_Return"]
    .mean()
    .unstack()
)

daily_long_short = daily_long_short.rename(
    columns={
        -1: "Short_Return",
        1: "Long_Return"
    }
)

daily_long_short["Long_Short_Return"] = (
    daily_long_short["Long_Return"]
    - daily_long_short["Short_Return"]
)





monthly_turnover = pd.read_csv("data/monthly_turnover.csv")

print("\nTransaction Costs")

print(
    monthly_turnover[
        ["Month", "Turnover", "Transaction_Cost"]
    ].describe()
)

print(
    f"\nTotal Transaction Costs: "
    f"{monthly_turnover['Transaction_Cost'].sum():.4%}"
)

print(
    f"Average Monthly Transaction Cost: "
    f"{monthly_turnover['Transaction_Cost'].mean():.4%}"
)

print("\nRaw Strategy Performance")

raw_cumulative = (
    1 + daily_long_short["Long_Short_Return"]
).cumprod()

raw_total_return = raw_cumulative.iloc[-1] - 1

print(f"Raw Total Return: {raw_total_return:.2%}")

daily_long_short["Year"] = daily_long_short.index.year

yearly_performance = (
    daily_long_short
    .groupby("Year")["Long_Short_Return"]
    .apply(lambda x: (1 + x).prod() - 1)
)

print("\nYearly Long-Short Performance")
print(yearly_performance)