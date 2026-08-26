import sqlite3
import pandas as pd

conn = sqlite3.connect("data/momentum.db")

with open("sql/analysis.sql", "r") as f:
    sql_script = f.read()

queries = [q.strip() for q in sql_script.split(";") if q.strip() and not q.strip().startswith("--")]

for i, query in enumerate(queries, 1):
    clean_query = "\n".join(
        line for line in query.split("\n") if not line.strip().startswith("--")
    ).strip()
    if not clean_query:
        continue
    print(f"\n--- Query {i} ---")
    try:
        result = pd.read_sql_query(clean_query, conn)
        print(result.head(10).to_string(index=False))
    except Exception as e:
        print(f"Error running query: {e}")

conn.close()