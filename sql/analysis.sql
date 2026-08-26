-- ============================================
-- Cross-Sectional Momentum: SQL Analysis
-- Run against data/momentum.db
-- ============================================

-- Monthly return per ticker --
SELECT
    Ticker,
    strftime('%Y-%m', Date) AS Month,
    (MAX(Close) - MIN(Close)) / MIN(Close) AS Approx_Monthly_Return
FROM market_data
GROUP BY Ticker, Month
ORDER BY Ticker, Month;

-- Average return by ticker across the full period --
SELECT
    Ticker,
    AVG(Close) AS Avg_Close_Price,
    COUNT(*) AS Trading_Days
FROM market_data
GROUP BY Ticker
ORDER BY Avg_Close_Price DESC;

-- Rank stocks by most recent momentum score --
SELECT
    Ticker,
    Date,
    Momentum_12_1,
    Momentum_Rank
FROM strategy_data
WHERE Date = (SELECT MAX(Date) FROM strategy_data)
  AND Momentum_12_1 IS NOT NULL
ORDER BY Momentum_Rank
LIMIT 20;

-- Turnover analysis: how many position changes per month --
SELECT
    strftime('%Y-%m', Date) AS Month,
    COUNT(DISTINCT Ticker) AS Active_Tickers,
    SUM(CASE WHEN Position = 1 THEN 1 ELSE 0 END) AS Long_Count,
    SUM(CASE WHEN Position = -1 THEN 1 ELSE 0 END) AS Short_Count
FROM strategy_data
WHERE Position IS NOT NULL AND Position != 0
GROUP BY Month
ORDER BY Month;

-- Data quality checks: missing / non-positive prices --
SELECT
    Ticker,
    COUNT(*) AS Rows_With_Bad_Price
FROM market_data
WHERE Close <= 0 OR Close IS NULL
GROUP BY Ticker;

-- Best and worst single trading days for the strategy --
SELECT
    Date,
    Net_Return
FROM backtest_results
ORDER BY Net_Return DESC
LIMIT 5;

SELECT
    Date,
    Net_Return
FROM backtest_results
ORDER BY Net_Return ASC
LIMIT 5;