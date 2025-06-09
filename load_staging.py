import pandas as pd
from sqlalchemy import create_engine

# 1. 配置数据库连接（替换密码或用户名）
DB_USER = 'mudihuang'
DB_PASS = ''
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'online_retail'
engine = create_engine(
    f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

# 2. 读取 CSV
csv_path = 'data/OnlineRetail.csv'  # 确保路径正确
df = pd.read_csv(csv_path, encoding='ISO-8859-1')

# 3. 基础清洗（可根据需要扩展）
df = df.dropna(subset=['CustomerID'])           # 删除没有 CustomerID 的行
df = df[(df.Quantity > 0) & (df.UnitPrice > 0)] # 过滤掉数量或单价 <= 0
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])  # 转成时间类型
df.columns = df.columns.str.lower()

# 4. 写入 staging_raw
df.to_sql('staging_raw', engine, if_exists='append', index=False)

print('导入完成，共写入 {:,} 行'.format(len(df)))
