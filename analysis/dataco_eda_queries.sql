-- DataCo Supply Chain Exploratory Data Analysis
-- Dialect: SQLite
-- Assumes the normalized tables created by analysis/generate_eda_summaries.py:
--   outputs/supply_chain_eda/dataco_supply_chain_eda.sqlite
--
-- Usage:
--   sqlite3 outputs/supply_chain_eda/dataco_supply_chain_eda.sqlite
--   .read sql/dataco_eda_queries.sql

.headers on
.mode column

-- 1) SCAN: Columns and coverage
SELECT
  COUNT(*) AS order_lines,
  COUNT(DISTINCT order_id) AS orders,
  COUNT(DISTINCT customer_id) AS customers,
  COUNT(DISTINCT product_name) AS products,
  COUNT(DISTINCT category_name) AS categories,
  MIN(order_ts) AS first_order_ts,
  MAX(order_ts) AS last_order_ts,
  ROUND(SUM(sales), 2) AS gross_sales,
  ROUND(SUM(order_profit_per_order), 2) AS profit,
  ROUND(SUM(order_profit_per_order) / SUM(sales), 4) AS profit_margin,
  ROUND(AVG(late_delivery_risk), 4) AS late_delivery_rate
FROM orders_clean;

-- 2) Data quality checks: fields/statuses that can change interpretation.
SELECT
  order_status,
  COUNT(DISTINCT order_id) AS orders,
  ROUND(SUM(sales), 2) AS sales,
  ROUND(SUM(sales) / (SELECT SUM(sales) FROM orders_clean), 4) AS sales_share
FROM orders_clean
GROUP BY order_status
ORDER BY sales DESC;

-- 3) Monthly trend: revenue, profit, AOV, and late delivery risk.
SELECT
  order_month,
  COUNT(DISTINCT order_id) AS orders,
  ROUND(SUM(sales), 2) AS sales,
  ROUND(SUM(order_profit_per_order), 2) AS profit,
  ROUND(SUM(order_profit_per_order) / SUM(sales), 4) AS profit_margin,
  ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS avg_order_value,
  ROUND(AVG(late_delivery_risk), 4) AS late_delivery_rate
FROM orders_clean
GROUP BY order_month
ORDER BY order_month;

-- 4) Yearly trend: treat 2018 as partial because it contains January only.
WITH yearly AS (
  SELECT
    order_year,
    ROUND(SUM(sales), 2) AS sales,
    ROUND(SUM(order_profit_per_order), 2) AS profit,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(AVG(late_delivery_risk), 4) AS late_delivery_rate
  FROM orders_clean
  GROUP BY order_year
)
SELECT
  order_year,
  sales,
  profit,
  orders,
  late_delivery_rate,
  ROUND((sales - LAG(sales) OVER (ORDER BY order_year)) / LAG(sales) OVER (ORDER BY order_year), 4) AS yoy_sales_pct
FROM yearly
ORDER BY order_year;

-- 5) Notable segments: top categories by sales and profit.
WITH category_perf AS (
  SELECT
    category_name,
    ROUND(SUM(sales), 2) AS sales,
    ROUND(SUM(order_profit_per_order), 2) AS profit,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(AVG(late_delivery_risk), 4) AS late_delivery_rate,
    ROUND(SUM(order_profit_per_order) / SUM(sales), 4) AS profit_margin,
    ROUND(SUM(sales) / (SELECT SUM(sales) FROM orders_clean), 4) AS sales_share
  FROM orders_clean
  GROUP BY category_name
)
SELECT *
FROM category_perf
ORDER BY sales DESC
LIMIT 15;

-- 6) Concentration check: how much do the largest eight categories drive?
WITH category_perf AS (
  SELECT
    category_name,
    SUM(sales) AS sales,
    SUM(order_profit_per_order) AS profit
  FROM orders_clean
  GROUP BY category_name
),
ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (ORDER BY sales DESC) AS sales_rank
  FROM category_perf
)
SELECT
  ROUND(SUM(CASE WHEN sales_rank <= 8 THEN sales END) / SUM(sales), 4) AS top_8_sales_share,
  ROUND(SUM(CASE WHEN sales_rank <= 8 THEN profit END) / SUM(profit), 4) AS top_8_profit_share
FROM ranked;

-- 7) Market and region view for finance / regional ops.
SELECT
  market,
  COUNT(DISTINCT order_id) AS orders,
  ROUND(SUM(sales), 2) AS sales,
  ROUND(SUM(order_profit_per_order), 2) AS profit,
  ROUND(SUM(order_profit_per_order) / SUM(sales), 4) AS profit_margin,
  ROUND(AVG(late_delivery_risk), 4) AS late_delivery_rate
FROM orders_clean
GROUP BY market
ORDER BY sales DESC;

SELECT
  order_region,
  market,
  COUNT(DISTINCT order_id) AS orders,
  ROUND(SUM(sales), 2) AS sales,
  ROUND(SUM(order_profit_per_order), 2) AS profit,
  ROUND(SUM(order_profit_per_order) / SUM(sales), 4) AS profit_margin,
  ROUND(AVG(late_delivery_risk), 4) AS late_delivery_rate
FROM orders_clean
GROUP BY order_region, market
HAVING orders >= 1000
ORDER BY sales DESC
LIMIT 15;

-- 8) Shipping promise risk: late-delivery rate by mode.
SELECT
  shipping_mode,
  COUNT(DISTINCT order_id) AS orders,
  COUNT(*) AS order_lines,
  ROUND(SUM(sales), 2) AS sales,
  ROUND(SUM(order_profit_per_order), 2) AS profit,
  ROUND(AVG(days_for_shipping_real), 2) AS avg_real_days,
  ROUND(AVG(days_for_shipment_scheduled), 2) AS avg_scheduled_days,
  ROUND(AVG(ship_delay_days), 2) AS avg_delay_days,
  ROUND(AVG(late_delivery_risk), 4) AS late_delivery_rate
FROM orders_clean
GROUP BY shipping_mode
ORDER BY late_delivery_rate DESC;

-- 9) Discount bands and margin pressure.
WITH discounted AS (
  SELECT
    CASE
      WHEN order_item_discount_rate <= 0.05 THEN '0-5%'
      WHEN order_item_discount_rate <= 0.10 THEN '5-10%'
      WHEN order_item_discount_rate <= 0.15 THEN '10-15%'
      WHEN order_item_discount_rate <= 0.20 THEN '15-20%'
      ELSE '20-25%'
    END AS discount_bin,
    sales,
    order_profit_per_order,
    late_delivery_risk
  FROM orders_clean
)
SELECT
  discount_bin,
  COUNT(*) AS order_lines,
  ROUND(SUM(sales), 2) AS sales,
  ROUND(SUM(order_profit_per_order), 2) AS profit,
  ROUND(SUM(order_profit_per_order) / SUM(sales), 4) AS profit_margin,
  ROUND(AVG(late_delivery_risk), 4) AS late_delivery_rate
FROM discounted
GROUP BY discount_bin
ORDER BY discount_bin;

-- 10) Product demand join: pageviews plus sales proxy.
WITH product_sales AS (
  SELECT
    product_key,
    product_name,
    category_name,
    ROUND(SUM(sales), 2) AS sales,
    ROUND(SUM(order_profit_per_order), 2) AS profit,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(AVG(late_delivery_risk), 4) AS late_delivery_rate
  FROM orders_clean
  GROUP BY product_key, product_name, category_name
),
product_views AS (
  SELECT
    product_key,
    product AS log_product_name,
    category AS log_category,
    department,
    COUNT(*) AS pageviews,
    COUNT(DISTINCT ip) AS unique_ips
  FROM access_logs_clean
  GROUP BY product_key, product, category, department
)
SELECT
  v.log_product_name,
  v.department,
  v.pageviews,
  v.unique_ips,
  s.category_name,
  s.orders,
  s.sales,
  s.profit,
  ROUND(s.sales / (v.pageviews / 1000.0), 2) AS sales_per_1k_views
FROM product_views v
JOIN product_sales s
  ON s.product_key = v.product_key
ORDER BY v.pageviews DESC
LIMIT 20;

-- 11) High-interest / low-sales proxy: product pages with many views but low sales per 1K views.
WITH product_sales AS (
  SELECT
    product_key,
    product_name,
    ROUND(SUM(sales), 2) AS sales,
    ROUND(SUM(order_profit_per_order), 2) AS profit,
    COUNT(DISTINCT order_id) AS orders
  FROM orders_clean
  GROUP BY product_key, product_name
),
product_views AS (
  SELECT
    product_key,
    product AS log_product_name,
    COUNT(*) AS pageviews,
    COUNT(DISTINCT ip) AS unique_ips
  FROM access_logs_clean
  GROUP BY product_key, product
)
SELECT
  v.log_product_name,
  v.pageviews,
  v.unique_ips,
  s.orders,
  s.sales,
  s.profit,
  ROUND(s.sales / (v.pageviews / 1000.0), 2) AS sales_per_1k_views
FROM product_views v
JOIN product_sales s
  ON s.product_key = v.product_key
WHERE v.pageviews >= 5000
ORDER BY sales_per_1k_views ASC
LIMIT 15;

-- 12) Access log seasonality and hourly behavior.
SELECT
  log_month,
  COUNT(*) AS pageviews,
  COUNT(DISTINCT ip) AS unique_ips
FROM access_logs_clean
GROUP BY log_month
ORDER BY log_month;

SELECT
  hour,
  COUNT(*) AS pageviews,
  COUNT(DISTINCT ip) AS unique_ips
FROM access_logs_clean
GROUP BY hour
ORDER BY pageviews DESC
LIMIT 10;
