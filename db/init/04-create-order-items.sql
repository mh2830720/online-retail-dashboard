DROP TABLE IF EXISTS fact_order_item;
CREATE TABLE fact_order_item AS
SELECT
  REGEXP_REPLACE("InvoiceNo", '\D', '', 'g')::INTEGER  AS order_id,
  "StockCode"                                        AS stock_code,
  ("Quantity" * "UnitPrice")::NUMERIC                AS line_total
FROM orders_stage;