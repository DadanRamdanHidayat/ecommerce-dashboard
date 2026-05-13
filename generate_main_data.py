"""
generate_main_data.py
---------------------
Jalankan script ini SEKALI untuk menghasilkan dashboard/main_data.csv
dari dataset mentah di folder data/.

Penggunaan:
    python generate_main_data.py
"""

import pandas as pd
import os

print("📦 Memuat dataset...")

customers_df      = pd.read_csv('data/customers_dataset.csv')
geolocation_df    = pd.read_csv('data/geolocation_dataset.csv')
order_items_df    = pd.read_csv('data/order_items_dataset.csv')
order_payments_df = pd.read_csv('data/order_payments_dataset.csv')
order_reviews_df  = pd.read_csv('data/order_reviews_dataset.csv')
orders_df         = pd.read_csv('data/orders_dataset.csv')
products_df       = pd.read_csv('data/products_dataset.csv')
category_df       = pd.read_csv('data/product_category_name_translation.csv')

print("🧹 Membersihkan data...")

# Konversi datetime
date_cols = [
    'order_purchase_timestamp','order_approved_at',
    'order_delivered_carrier_date','order_delivered_customer_date',
    'order_estimated_delivery_date'
]
for col in date_cols:
    orders_df[col] = pd.to_datetime(orders_df[col])

order_reviews_df['review_creation_date']    = pd.to_datetime(order_reviews_df['review_creation_date'])
order_reviews_df['review_answer_timestamp'] = pd.to_datetime(order_reviews_df['review_answer_timestamp'])
order_items_df['shipping_limit_date']       = pd.to_datetime(order_items_df['shipping_limit_date'])

# Drop duplikat geolokasi
geolocation_df.drop_duplicates(
    subset=['geolocation_zip_code_prefix','geolocation_lat','geolocation_lng'],
    inplace=True
)

# Isi missing
products_df['product_category_name'].fillna('unknown', inplace=True)

# Hanya pesanan delivered
orders_delivered = orders_df[orders_df['order_status'] == 'delivered'].copy()

print("🔗 Menggabungkan dataset...")

# Tambah terjemahan kategori
products_df = products_df.merge(category_df, on='product_category_name', how='left')
products_df['product_category_name_english'].fillna(
    products_df['product_category_name'], inplace=True
)

# Merge bertahap
master = orders_delivered.merge(customers_df, on='customer_id', how='left')
master = master.merge(order_items_df, on='order_id', how='left')
master = master.merge(
    products_df[['product_id','product_category_name_english']],
    on='product_id', how='left'
)

# Agregasi pembayaran
payment_agg = order_payments_df.groupby('order_id').agg(
    payment_value=('payment_value','sum'),
    payment_type=('payment_type', lambda x: x.mode()[0])
).reset_index()
master = master.merge(payment_agg, on='order_id', how='left')

# Review score
reviews_first = order_reviews_df.sort_values('review_creation_date') \
    .drop_duplicates('order_id')
master = master.merge(
    reviews_first[['order_id','review_score']],
    on='order_id', how='left'
)

print(f"✅ Master DataFrame: {master.shape}")

# Simpan ke dashboard/
os.makedirs('dashboard', exist_ok=True)
master.to_csv('dashboard/main_data.csv', index=False)

print("💾 dashboard/main_data.csv berhasil disimpan!")
print("🚀 Sekarang jalankan: streamlit run dashboard/dashboard.py")
