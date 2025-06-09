# app.py

import os
import streamlit as st
import pandas as pd
import redis
from sqlalchemy import create_engine
from datetime import date, timedelta
import altair as alt  # Altair for interactive charts


try:
    from prophet import Prophet
    has_prophet = True
except ImportError:
    has_prophet = False

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Postgres connection from env
DB_URI = os.getenv('DB_URI', 'postgresql://mudihuang@db:5432/online_retail')
engine = create_engine(DB_URI)

# Helper: fetch daily sales, with Redis caching
def get_daily_sales(sale_date: date) -> pd.DataFrame:
    if sale_date is None:
        return pd.DataFrame([])

    key = f"daily_sales:{sale_date.isoformat()}"
    cached = r.get(key)
    if cached:
        return pd.read_json(cached.decode('utf-8'), orient='split')

    sql = f"""
    SELECT sale_date, orders, revenue, units_sold
    FROM mv_daily_sales
    WHERE sale_date = '{sale_date.isoformat()}';
    """
    df = pd.read_sql_query(sql, engine)
    # Cache for 1 hour
    if not df.empty:
        r.set(key, df.to_json(date_format='iso', orient='split'), ex=3600)
    return df


dates = pd.read_sql_query(
    "SELECT MIN(sale_date) AS min_date, MAX(sale_date) AS max_date FROM mv_daily_sales;",
    engine
)
min_date = dates.loc[0, 'min_date']
max_date = dates.loc[0, 'max_date']


if pd.isnull(min_date) or pd.isnull(max_date):
    st.title("Daily Sales Dashboard")
    st.error("No sales data available in mv_daily_sales. Please check your data and initialization scripts.")
    st.stop()


min_date = pd.to_datetime(min_date).date()
max_date = pd.to_datetime(max_date).date()

# Check if geography data exists
def can_do_geography():
    df = pd.read_sql_query(
        "SELECT COUNT(DISTINCT country) AS cnt FROM dim_customer WHERE country IS NOT NULL;",
        engine
    )
    return df.loc[0, 'cnt'] > 0

st.title("Daily Sales Dashboard")

dt = st.date_input(
    "Select date", 
    value=max_date, 
    min_value=min_date, 
    max_value=max_date
)

# Daily summary
sales_df = get_daily_sales(dt)
st.subheader(f"Sales overview for {dt}")
if sales_df.empty:
    st.warning("No sales data for this date.")
else:
    sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date']).dt.date
    st.table(sales_df)

# Recent 7-day trend
st.subheader("Recent 7 Days Sales Trend")
trend_start = dt - timedelta(days=6) if dt else None
if trend_start:
    trend_query = f"""
    SELECT sale_date, orders, revenue, units_sold
    FROM mv_daily_sales
    WHERE sale_date BETWEEN '{trend_start}' AND '{dt}'
    ORDER BY sale_date;
    """
    trend_df = pd.read_sql_query(trend_query, engine)
    trend_df['sale_date'] = pd.to_datetime(trend_df['sale_date'])
    trend_df = trend_df.set_index('sale_date')
    if not trend_df.empty:
        st.line_chart(trend_df)
    else:
        st.warning("No sales data in the past 7 days.")

# RFM segmentation
st.subheader("RFM Customer Segmentation")
rfm_sql = f"""
SELECT
  o.customer_id,
  DATE_PART(
    'day',
    '2011-12-09'::date - MAX(o.invoice_date)
  ) AS recency,
  COUNT(DISTINCT o.order_id) AS frequency,
  SUM(i.line_total)         AS monetary
FROM fact_order o
JOIN fact_order_item i 
  ON o.order_id = i.order_id
GROUP BY o.customer_id;

"""
rfm_df = pd.read_sql_query(rfm_sql, engine).dropna()
st.dataframe(rfm_df.head(10))
if not rfm_df.empty:
    chart = alt.Chart(rfm_df).mark_circle(size=100).encode(
        x=alt.X('customer_id:N', scale=alt.Scale(zero=False)),
        y=alt.Y('monetary:Q', scale=alt.Scale(zero=False)),
        tooltip=['recency','frequency','monetary']
    ).properties(width=600, height=400)
    st.altair_chart(chart, use_container_width=True)

# Forecast & anomaly detection
st.subheader("Sales Forecast & Anomaly Detection")
full_df = pd.read_sql_query("SELECT * FROM mv_daily_sales ORDER BY sale_date;", engine)
full_df['sale_date'] = pd.to_datetime(full_df['sale_date'])
full_df = full_df.set_index('sale_date')
if has_prophet and not full_df.empty:
    prophet_df = full_df['revenue'].reset_index().rename(columns={'sale_date':'ds','revenue':'y'})
    m = Prophet()
    m.fit(prophet_df)
    future = m.make_future_dataframe(periods=7)
    forecast = m.predict(future).set_index('ds')
    df_plot = full_df.join(forecast[['yhat','yhat_lower','yhat_upper']], how='left').reset_index()
    df_plot['anomaly'] = (
        (df_plot['revenue'] > df_plot['yhat_upper']) |
        (df_plot['revenue'] < df_plot['yhat_lower'])
    )
    band = alt.Chart(df_plot).mark_area(opacity=0.2).encode(
        x='sale_date:T', y='yhat_lower:Q', y2='yhat_upper:Q'
    )
    pred_line = alt.Chart(df_plot).mark_line().encode(
        x='sale_date:T', y='yhat:Q', tooltip=['sale_date','yhat']
    )
    actual = alt.Chart(df_plot).mark_circle(size=60).encode(
        x='sale_date:T', y='revenue:Q',
        color=alt.condition('datum.anomaly', alt.value('red'), alt.value('black')),
        tooltip=['sale_date','revenue','yhat_lower','yhat_upper']
    )
    st.altair_chart((band + pred_line + actual).properties(width=700, height=300), use_container_width=True)
    anomalies = df_plot[df_plot['anomaly']]
    if not anomalies.empty:
        st.subheader("Anomalies Detected")
        st.table(anomalies[['sale_date','revenue','yhat','yhat_lower','yhat_upper']])
else:
    st.info("Prophet not installed or no data for forecasting.")

# Geography check
st.subheader("Geography Check")
if can_do_geography():
    country_sales = pd.read_sql_query(
        "SELECT c.country, SUM(i.line_total) AS revenue FROM fact_order_item i \
         JOIN fact_order o USING(order_id) \
         JOIN dim_customer c ON o.customer_id=c.customer_id \
         WHERE c.country IS NOT NULL GROUP BY c.country;",
        engine
    )
    country_series = country_sales.set_index('country')['revenue']
    st.bar_chart(country_series)
else:
    st.warning("No valid country data in dim_customer. Cannot display geography.")

# All-time trend
st.subheader("All-time Sales Trend")
st.line_chart(full_df[['revenue','units_sold']])
