DROP MATERIALIZED VIEW IF EXISTS mv_daily_sales;
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT
  sale_date,
  COUNT(order_id)       AS orders,
  SUM(amount)::numeric  AS revenue,
  SUM(quantity)::bigint AS units_sold
FROM fact_order
GROUP BY sale_date
WITH NO DATA;

REFRESH MATERIALIZED VIEW mv_daily_sales;
