import pandas as pd
import matplotlib.pyplot as plt

results = pd.read_csv("data/parameter_research.csv")

long_short = results[results["Type"] == "Long-Short"]

pivot = long_short.pivot(index="Lookback", columns="Portfolio", values="Sharpe")

fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(pivot.values, cmap="RdYlGn", aspect="auto")

ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(pivot.columns)
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(pivot.index)

ax.set_xlabel("Portfolio Size")
ax.set_ylabel("Momentum Lookback")
ax.set_title("Sharpe Ratio by Lookback and Portfolio Size")

for i in range(len(pivot.index)):
    for j in range(len(pivot.columns)):
        value = pivot.values[i, j]
        ax.text(j, i, f"{value:.2f}", ha="center", va="center", color="black")

fig.colorbar(im, ax=ax, label="Sharpe Ratio")
plt.tight_layout()
plt.savefig("data/chart_parameter_heatmap.png")
plt.show()