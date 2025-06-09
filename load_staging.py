import pandas as pd
from sqlalchemy import create_engine

DB_USER = 'mudihuang'
DB_PASS = ''
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'online_retail'
engine = create_engine(
    f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

csv_path = 'data/OnlineRetail.csv'
df = pd.read_csv(csv_path, encoding='ISO-8859-1')

df = df.dropna(subset=['CustomerID'])
df = df[(df.Quantity > 0) & (df.UnitPrice > 0)]
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df.columns = df.columns.str.lower()

df.to_sql('staging_raw', engine, if_exists='append', index=False)

print('Import finished. Total {:,} lines'.format(len(df)))
