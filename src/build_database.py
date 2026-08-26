import sqlite3
import pandas as pd

market_data = pd.read_csv("data/market_data.csv")
backtest_results = pd.read_csv("data/backtest_results.csv")
strategy_data = pd.read_csv("data/strategy_data.csv")

conn = sqlite3.connect("data/momentum.db")

market_data.to_sql("market_data", conn, if_exists="replace", index=False)
backtest_results.to_sql("backtest_results", conn, if_exists="replace", index=False)
strategy_data.to_sql("strategy_data", conn, if_exists="replace", index=False)

conn.close()
print("Database created at data/momentum.db")