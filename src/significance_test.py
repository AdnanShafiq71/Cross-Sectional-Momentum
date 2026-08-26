import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm

data = pd.read_csv("data/backtest_results.csv")
data["Date"] = pd.to_datetime(data["Date"])

returns = data["Net_Return"].dropna()


returns = data["Net_Return"].dropna()

# ---------- Simple t-test (assumes returns are independent) ----------
mean_daily_return = returns.mean()
t_stat, p_value = stats.ttest_1samp(returns, 0)

# ---------- Newey-West t-test (accounts for autocorrelation) ----------
# Regress returns on a constant only - the constant's t-stat with
# HAC (Newey-West) standard errors is the robust significance test.
X = np.ones(len(returns))
model = sm.OLS(returns, X)
nw_results = model.fit(cov_type="HAC", cov_kwds={"maxlags": 5})

nw_t_stat = nw_results.tvalues.iloc[0]
nw_p_value = nw_results.pvalues.iloc[0]

annualised_return = (1 + mean_daily_return) ** 252 - 1
annualised_vol = returns.std() * (252 ** 0.5)

print("========== STATISTICAL SIGNIFICANCE ==========")
print(f"Mean Daily Return: {mean_daily_return:.5%}")
print(f"Annualised Return: {annualised_return:.2%}")
print(f"Annualised Volatility: {annualised_vol:.2%}")
print(f"Number of Observations: {len(returns)}")

print("\n--- Standard t-test ---")
print(f"t-statistic: {t_stat:.3f}")
print(f"p-value: {p_value:.4f}")

print("\n--- Newey-West (HAC) t-test ---")
print(f"t-statistic: {nw_t_stat:.3f}")
print(f"p-value: {nw_p_value:.4f}")

if nw_p_value < 0.05:
    print("\nResult: statistically significant at the 5% level.")
else:
    print("\nResult: NOT statistically significant at the 5% level "
          "- cannot reject the hypothesis that true return is zero.")