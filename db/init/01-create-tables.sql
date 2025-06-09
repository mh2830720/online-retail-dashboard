-- db/init/01-create-tables.sql

DROP TABLE IF EXISTS fact_order;
CREATE TABLE fact_order (
  order_id     SERIAL      PRIMARY KEY,
  customer_id  INTEGER     NOT NULL,
  invoice_date TIMESTAMP   NOT NULL,
  sale_date    DATE        NOT NULL,
  amount       NUMERIC(10,2) NOT NULL
);