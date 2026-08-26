import pandas as pd
import matplotlib.pyplot as plt

strategy_data = pd.read_csv("data/strategy_data.csv")
strategy_data["Date"] = pd.to_datetime(strategy_data["Date"])
strategy_data["Month"] = strategy_data["Date"].dt.to_period("M")

monthly_positions = (
    strategy_data[strategy_data["Momentum_Rank"].notna()]
    .sort_values(["Ticker", "Date"])
    .groupby(["Ticker", "Month"])["Position"]
    .last()
    .reset_index()
)

monthly_positions["Previous_Position"] = (
    monthly_positions.groupby("Ticker")["Position"].shift(1)
)

monthly_positions["Position_Change"] = (
    monthly_positions["Position"] - monthly_positions["Previous_Position"]
)

monthly_positions["Turnover"] = monthly_positions["Position_Change"].abs() / 10

monthly_turnover = (
    monthly_positions.groupby("Month")["Turnover"].sum() / 2
).reset_index()

daily_returns = (
    strategy_data[strategy_data["Position"].notna() & (strategy_data["Position"] != 0)]
    .groupby("Date")
    .apply(lambda x: pd.Series({
        "Long_Return": x.loc[x["Position"] == 1, "Daily_Return"].mean(),
        "Short_Return": x.loc[x["Position"] == -1, "Daily_Return"].mean()
    }))
    .reset_index()
)

daily_returns["Long_Short_Return"] = (
    daily_returns["Long_Return"] - daily_returns["Short_Return"]
)
daily_returns["Month"] = pd.to_datetime(daily_returns["Date"]).dt.to_period("M")

daily_returns = daily_returns.merge(
    monthly_turnover, on="Month", how="left"
)

daily_returns["Is_First_Day_Of_Month"] = (
    daily_returns["Month"] != daily_returns["Month"].shift(1)
)


def backtest_at_cost(cost_rate_bps):
    cost_rate = cost_rate_bps / 10000
    turnover_cost = daily_returns["Turnover"] * cost_rate
    turnover_cost = turnover_cost.where(daily_returns["Is_First_Day_Of_Month"], 0)

    net_return = daily_returns["Long_Short_Return"] - turnover_cost
    cumulative = (1 + net_return).cumprod()

    total_return = cumulative.iloc[-1] - 1
    years = (
        daily_returns["Date"].max() - daily_returns["Date"].min()
    ) if isinstance(daily_returns["Date"].max(), pd.Timestamp) else None

    dates = pd.to_datetime(daily_returns["Date"])
    years = (dates.max() - dates.min()).days / 365.25
    annual_return = (1 + total_return) ** (1 / years) - 1
    annual_vol = net_return.std() * (252 ** 0.5)

    risk_free_daily = 1.04 ** (1 / 252) - 1
    excess = net_return - risk_free_daily
    sharpe = excess.mean() / excess.std() * (252 ** 0.5)

    return total_return, annual_return, sharpe


cost_levels_bps = [0, 5, 10, 25, 50]
results = []

for cost in cost_levels_bps:
    total_ret, annual_ret, sharpe = backtest_at_cost(cost)
    results.append({
        "Cost_bps": cost,
        "Total_Return": total_ret,
        "Annual_Return": annual_ret,
        "Sharpe": sharpe
    })

results_df = pd.DataFrame(results)
results_df.to_csv("data/cost_sensitivity.csv", index=False)
print(results_df.to_string(index=False))

plt.figure(figsize=(10, 6))
plt.plot(results_df["Cost_bps"], results_df["Sharpe"], marker="o")
plt.title("Transaction Cost Sensitivity")
plt.xlabel("Transaction Cost (basis points per trade)")
plt.ylabel("Sharpe Ratio")
plt.grid(True)
plt.savefig("data/chart_cost_sensitivity.png")
plt.show()