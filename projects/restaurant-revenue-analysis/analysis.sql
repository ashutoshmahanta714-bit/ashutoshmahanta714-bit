-- SQLite: import data/tips.csv as tips, then run these queries.
-- Grain: one restaurant bill. No date or location exists in this dataset.
SELECT COUNT(*) AS bills, ROUND(SUM(total_bill),2) AS revenue,
       ROUND(AVG(total_bill),2) AS average_bill,
       ROUND(SUM(tip)/SUM(total_bill)*100,2) AS weighted_tip_rate_pct
FROM tips;

SELECT day, COUNT(*) AS bills, ROUND(SUM(total_bill),2) AS revenue,
       ROUND(AVG(total_bill),2) AS average_bill,
       ROUND(SUM(tip)/SUM(total_bill)*100,2) AS weighted_tip_rate_pct
FROM tips GROUP BY day ORDER BY revenue DESC;

SELECT time, size AS party_size, COUNT(*) AS bills,
       ROUND(AVG(total_bill),2) AS average_bill,
       ROUND(SUM(total_bill),2) AS revenue
FROM tips GROUP BY time, size HAVING COUNT(*) >= 5
ORDER BY time, party_size;

SELECT day, time, COUNT(*) AS bills,
       ROUND(AVG(total_bill),2) AS average_bill
FROM tips GROUP BY day, time ORDER BY day, time;
