-- db/init/02-load-orders.sql

-- 1) create a staging table whose columns match exactly the CSV header
CREATE TABLE orders_stage (
  "InvoiceNo"    TEXT,
  "StockCode"    TEXT,
  "Description"  TEXT,
  "Quantity"     INTEGER,
  "InvoiceDate"  TEXT,    -- we’ll parse this into a DATE
  "UnitPrice"    NUMERIC,
  "CustomerID"   TEXT,
  "Country"      TEXT
);

-- 2) bulk‐load the raw CSV
SET client_encoding = 'LATIN1';

COPY orders_stage
  FROM '/docker-entrypoint-initdb.d/OnlineRetail.csv'
  WITH (
    FORMAT csv,
    HEADER true
    -- you can also do: ENCODING 'LATIN1'
  );

-- 2) drop any old fact_order
DROP TABLE IF EXISTS fact_order;

-- 3) create & populate in one go:
CREATE TABLE fact_order AS
SELECT
  CAST("InvoiceNo"    AS INTEGER)                   AS order_id,
  CAST("CustomerID"   AS INTEGER)                   AS customer_id,
  to_timestamp("InvoiceDate",'MM/DD/YYYY HH24:MI')  AS invoice_date,
  to_timestamp("InvoiceDate",'MM/DD/YYYY HH24:MI')::date AS sale_date,
  ("UnitPrice" * "Quantity")::NUMERIC               AS amount,
  "Quantity"                                                AS quantity
FROM orders_stage
WHERE "InvoiceNo" ~ '^[0-9]+$';