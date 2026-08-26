import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---------- Load data ----------
data = pd.read_csv("data/backtest_results.csv")
strategy_data = pd.read_csv("data/strategy_data.csv")
monthly_turnover = pd.read_csv("data/monthly_turnover.csv")
spy = pd.read_csv("data/spy_data.csv")

data["Date"] = pd.to_datetime(data["Date"])
strategy_data["Date"] = pd.to_datetime(strategy_data["Date"])
spy["Date"] = pd.to_datetime(spy["Date"])

# ---------- Benchmark ----------
spy = spy.sort_values("Date")
spy["Benchmark_Return"] = spy["SPY_Close"].pct_change()
spy = spy[spy["Date"] >= data["Date"].min()].copy()
spy["Benchmark_Cumulative"] = (1 + spy["Benchmark_Return"]).cumprod()

# ---------- Core performance metrics ----------
risk_free_rate_annual = 0.04
risk_free_rate_daily = (1 + risk_free_rate_annual) ** (1 / 252) - 1

returns = data["Net_Return"]
excess_returns = returns - risk_free_rate_daily

total_return = data["Cumulative_Return"].iloc[-1] - 1

years = (data["Date"].iloc[-1] - data["Date"].iloc[0]).days / 365.25
cagr = (1 + total_return) ** (1 / years) - 1

annual_vol = returns.std() * (252 ** 0.5)

sharpe_ratio = excess_returns.mean() / excess_returns.std() * (252 ** 0.5)

downside_returns = excess_returns[excess_returns < 0]
downside_vol = downside_returns.std() * (252 ** 0.5)
sortino_ratio = (excess_returns.mean() * 252) / downside_vol

running_max = data["Cumulative_Return"].cummax()
drawdown = data["Cumulative_Return"] / running_max - 1
max_drawdown = drawdown.min()

calmar_ratio = cagr / abs(max_drawdown)

# ---------- Portfolio stats ----------
position_counts = (
    strategy_data[strategy_data["Position"].isin([-1, 1])]
    .groupby(["Date", "Position"])
    .size()
    .unstack(fill_value=0)
)

avg_long_positions = position_counts.get(1, pd.Series(dtype=float)).mean()
avg_short_positions = position_counts.get(-1, pd.Series(dtype=float)).mean()

avg_monthly_turnover = monthly_turnover["Turnover"].mean()
total_transaction_costs = monthly_turnover["Transaction_Cost"].sum()

# ---------- Long vs short ----------
daily_long_short = (
    strategy_data[strategy_data["Position"].isin([-1, 1])]
    .groupby(["Date", "Position"])["Daily_Return"]
    .mean()
    .unstack()
    .rename(columns={-1: "Short_Return", 1: "Long_Return"})
)

daily_long_short["Long_Cumulative"] = (1 + daily_long_short["Long_Return"]).cumprod()
daily_long_short["Short_Cumulative"] = (1 + daily_long_short["Short_Return"]).cumprod()

long_total_return = daily_long_short["Long_Cumulative"].iloc[-1] - 1
short_total_return = daily_long_short["Short_Cumulative"].iloc[-1] - 1

long_vol = daily_long_short["Long_Return"].std() * (252 ** 0.5)
short_vol = daily_long_short["Short_Return"].std() * (252 ** 0.5)

# ---------- Yearly & monthly performance ----------
data["Year"] = data["Date"].dt.year
data["YearMonth"] = data["Date"].dt.to_period("M")

yearly_performance = data.groupby("Year")["Net_Return"].apply(lambda x: (1 + x).prod() - 1)
monthly_performance = data.groupby("YearMonth")["Net_Return"].apply(lambda x: (1 + x).prod() - 1)

# ---------- Print report ----------
print("========== PERFORMANCE ==========")
print(f"Total Return: {total_return:.2%}")
print(f"CAGR: {cagr:.2%}")
print(f"Annualised Volatility: {annual_vol:.2%}")
print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
print(f"Sortino Ratio: {sortino_ratio:.2f}")
print(f"Maximum Drawdown: {max_drawdown:.2%}")
print(f"Calmar Ratio: {calmar_ratio:.2f}")

print("\n========== PORTFOLIO ==========")
print(f"Avg Long Positions: {avg_long_positions:.1f}")
print(f"Avg Short Positions: {avg_short_positions:.1f}")
print(f"Avg Monthly Turnover: {avg_monthly_turnover:.2%}")
print(f"Total Transaction Costs (cumulative): {total_transaction_costs:.2%}")

print("\n========== BENCHMARK ==========")
spy_total_return = spy["Benchmark_Cumulative"].iloc[-1] - 1
print(f"Strategy Total Return: {total_return:.2%}")
print(f"S&P 500 Total Return: {spy_total_return:.2%}")

print("\n========== LONG VS SHORT ==========")
print(f"Long Leg Total Return: {long_total_return:.2%}")
print(f"Short Leg Total Return: {short_total_return:.2%}")
print(f"Long Leg Volatility: {long_vol:.2%}")
print(f"Short Leg Volatility: {short_vol:.2%}")

print("\n========== YEARLY PERFORMANCE ==========")
print(yearly_performance)

print("\n========== MONTHLY PERFORMANCE ==========")
print(monthly_performance)

# ---------- Charts ----------

# Chart 1: Equity curve
plt.figure(figsize=(10, 6))
plt.plot(data["Date"], data["Cumulative_Return"], label="Momentum Strategy")
plt.plot(spy["Date"], spy["Benchmark_Cumulative"], label="S&P 500 (SPY)")
plt.title("Momentum Strategy vs S&P 500")
plt.xlabel("Date")
plt.ylabel("Growth of £1")
plt.legend()
plt.grid(True)
plt.savefig("data/chart_equity_curve.png")
plt.show()

# Chart 2: Drawdown
plt.figure(figsize=(10, 6))
plt.plot(data["Date"], drawdown)
plt.title("Strategy Drawdown")
plt.xlabel("Date")
plt.ylabel("Drawdown")
plt.grid(True)
plt.savefig("data/chart_drawdown.png")
plt.show()

# Chart 3: Annual returns
plt.figure(figsize=(10, 6))
yearly_performance.plot(kind="bar")
plt.title("Yearly Strategy Returns")
plt.xlabel("Year")
plt.ylabel("Return")
plt.grid(True)
plt.savefig("data/chart_annual_returns.png")
plt.show()

# Chart 4: Long vs short cumulative performance
plt.figure(figsize=(10, 6))
plt.plot(daily_long_short.index, daily_long_short["Long_Cumulative"], label="Long Leg")
plt.plot(daily_long_short.index, daily_long_short["Short_Cumulative"], label="Short Leg")
plt.title("Long vs Short Leg Performance")
plt.xlabel("Date")
plt.ylabel("Growth of £1")
plt.legend()
plt.grid(True)
plt.savefig("data/chart_long_vs_short.png")
plt.show()

print("\n========== ANALYSIS COMPLETE ==========")