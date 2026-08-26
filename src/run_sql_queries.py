import sqlite3
import pandas as pd

conn = sqlite3.connect("data/momentum.db")

with open("sql/analysis.sql", "r") as f:
    lines = f.readlines()

sql_lines = [
    line for line in lines
    if not line.strip().startswith("--") and line.strip() != ""
]

sql_no_comments = "\n".join(sql_lines)

queries = [q.strip() for q in sql_no_comments.split(";") if q.strip()]

print(f"Found {len(queries)} queries to run.\n")

for i, query in enumerate(queries, 1):
    print(f"--- Query {i} ---")
    try:
        result = pd.read_sql_query(query, conn)
        print(result.head(10).to_string(index=False))
    except Exception as e:
        print(f"Error running query: {e}")
    print()

conn.close()