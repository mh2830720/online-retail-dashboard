# app.py

import streamlit as st
import pandas as pd
import redis
from sqlalchemy import create_engine
from datetime import date, timedelta
import altair as alt  # Altair for interactive charts

# 可选：用于预测
try:
    from prophet import Prophet
    has_prophet = True
except ImportError:
    has_prophet = False

# Redis 连接
r = redis.Redis(host='localhost', port=6379, db=0)
# PostgreSQL 连接字符串
DB_URI = 'postgresql://mudihuang@localhost:5432/online_retail'
engine = create_engine(DB_URI)

# 辅助函数：获取每天汇总
def get_daily_sales(sale_date: date) -> pd.DataFrame:
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
    r.set(key, df.to_json(date_format='iso', orient='split'), ex=3600)
    return df

# 获取可用日期范围
min_date = pd.read_sql_query("SELECT MIN(sale_date) AS d FROM mv_daily_sales;", engine).loc[0,'d']
max_date = pd.read_sql_query("SELECT MAX(sale_date) AS d FROM mv_daily_sales;", engine).loc[0,'d']

def can_do_geography():
    df = pd.read_sql_query("SELECT COUNT(DISTINCT country) AS cnt FROM dim_customer WHERE country IS NOT NULL;", engine)
    return df.loc[0,'cnt'] > 0

# 页面标题
st.title("Daily Sales Dashboard")
# 日期选择
dt = st.date_input("选择日期", value=max_date, min_value=min_date, max_value=max_date)

# 当天汇总
sales_df = get_daily_sales(dt)
st.subheader(f"{dt} 销售概览")
if sales_df.empty:
    st.warning("该天无销售数据")
else:
    sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'])
    st.table(sales_df)

# 最近7天趋势
st.subheader("Recent 7 Days Sales Trend")
trend_query = f"""
SELECT sale_date, orders, revenue, units_sold
FROM mv_daily_sales
WHERE sale_date BETWEEN '{dt - timedelta(days=6)}' AND '{dt}'
ORDER BY sale_date;
"""
trend_df = pd.read_sql_query(trend_query, engine)
trend_df['sale_date'] = pd.to_datetime(trend_df['sale_date'])
trend_df = trend_df.set_index('sale_date')
if not trend_df.empty:
    st.line_chart(trend_df)
else:
    st.warning("过去7天无销售数据")

# RFM 客户细分，recency 基于选定日期
st.subheader("RFM Customer Segmentation")
rfm_sql = f"""
SELECT
o.customerid,
DATE_PART('day','{dt.isoformat()}'::date - MAX(o.invoicedate)) AS recency,
COUNT(DISTINCT o.orderid) AS frequency,
SUM(i.linetotal) AS monetary
FROM fact_order o
JOIN fact_order_item i USING(orderid)
GROUP BY o.customerid;
"""
rfm_df = pd.read_sql_query(rfm_sql, engine)
rfm_df = rfm_df.dropna()
st.dataframe(rfm_df.head(10))
if not rfm_df.empty:
    chart = alt.Chart(rfm_df).mark_circle(size=100).encode(
        x=alt.X('recency:Q', scale=alt.Scale(zero=False)),
        y=alt.Y('monetary:Q', scale=alt.Scale(zero=False)),
        color=alt.value('#1f77b4'),
        tooltip=['customerid','recency','frequency','monetary']
    ).properties(width=600, height=400)
    st.altair_chart(chart, use_container_width=True)

# 预测与异常检测
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
    df_plot['anomaly'] = (df_plot['revenue'] > df_plot['yhat_upper']) | (df_plot['revenue'] < df_plot['yhat_lower'])
    band = alt.Chart(df_plot).mark_area(opacity=0.2).encode(
        x='sale_date:T', y='yhat_lower:Q', y2='yhat_upper:Q'
    )
    pred_line = alt.Chart(df_plot).mark_line(color='blue').encode(
        x='sale_date:T', y='yhat:Q', tooltip=['sale_date','yhat'])
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
    st.info("Prophet 未安装或无数据，无法执行预测")

# 地理分布检查
st.subheader("Geography Check")
if can_do_geography():
    country_sales = pd.read_sql_query(
        "SELECT c.country, SUM(i.linetotal) AS revenue FROM fact_order_item i JOIN fact_order o USING(orderid) JOIN dim_customer c ON o.customerid=c.customerid WHERE c.country IS NOT NULL GROUP BY c.country;", engine
    )
    country_series = country_sales.set_index('country')['revenue']
    st.bar_chart(country_series)
else:
    st.warning("dim_customer 中无有效 country 数据，无法做地理分布分析")

# 全时段趋势
st.subheader("All-time Sales Trend")
st.line_chart(full_df[['revenue','units_sold']])
