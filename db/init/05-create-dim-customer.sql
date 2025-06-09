-- db/init/05-create-dim-customer.sql
DROP TABLE IF EXISTS dim_customer;

CREATE TABLE dim_customer AS
SELECT DISTINCT
  CAST("CustomerID" AS INTEGER) AS customer_id,
  "Country"                  AS country
FROM orders_stage
WHERE "CustomerID" IS NOT NULL AND "CustomerID" <> '';
