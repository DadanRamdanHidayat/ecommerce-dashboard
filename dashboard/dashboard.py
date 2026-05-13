import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import warnings

warnings.filterwarnings('ignore')

# ── Konfigurasi halaman ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        color: #f8fafc;
    }
    .metric-card .label {
        font-size: 12px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    .metric-card .value {
        font-size: 28px;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-card .delta {
        font-size: 12px;
        color: #4ade80;
        margin-top: 4px;
    }
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #1e293b;
        border-left: 4px solid #38bdf8;
        padding-left: 12px;
        margin: 24px 0 16px 0;
    }
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    div[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    main      = pd.read_csv('dashboard/main_data.csv', parse_dates=['order_purchase_timestamp'])
    payments  = pd.read_csv('data/order_payments_dataset.csv')
    geo       = pd.read_csv('data/geolocation_dataset.csv')
    customers = pd.read_csv('data/customers_dataset.csv')
    sellers   = pd.read_csv('data/sellers_dataset.csv')
    return main, payments, geo, customers, sellers

try:
    main_df, payments_df, geo_df, customers_df, sellers_df = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"❌ Gagal memuat data: {e}")
    st.info("Pastikan file `dashboard/main_data.csv` dan dataset lainnya tersedia.")
    data_loaded = False

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛒 E-Commerce\nAnalytics Dashboard")
    st.markdown("---")

    if data_loaded:
        min_date = main_df['order_purchase_timestamp'].min().date()
        max_date = main_df['order_purchase_timestamp'].max().date()

        st.markdown("### 📅 Filter Tanggal")
        start_date = st.date_input("Dari", value=min_date, min_value=min_date, max_value=max_date)
        end_date   = st.date_input("Sampai", value=max_date, min_value=min_date, max_value=max_date)

        st.markdown("### 📌 Navigasi")
        page = st.radio("Pilih Halaman:", [
            "📊 Overview",
            "🏷️ Produk & Kategori",
            "⭐ Ulasan Pelanggan",
            "💳 Pembayaran",
            "👥 RFM Analysis",
            "🗺️ Geospatial",
            "🔵 Clustering"
        ])
    else:
        page = "📊 Overview"

    st.markdown("---")
    st.markdown("<small>© 2026 E-Commerce Analytics</small>", unsafe_allow_html=True)

# ── Filter data berdasarkan tanggal ──────────────────────────────────────────
if data_loaded:
    mask = (
        (main_df['order_purchase_timestamp'].dt.date >= start_date) &
        (main_df['order_purchase_timestamp'].dt.date <= end_date)
    )
    df = main_df[mask].copy()
    df['order_year_month'] = df['order_purchase_timestamp'].dt.to_period('M')

# ── HALAMAN: Overview ────────────────────────────────────────────────────────
if page == "📊 Overview":
    st.title("📊 Overview — E-Commerce Brasil")
    st.caption("Analisis menyeluruh performa platform e-commerce Brazil")

    if not data_loaded:
        st.warning("Data belum tersedia.")
        st.stop()

    # KPI Cards
    total_orders   = df['order_id'].nunique()
    total_revenue  = df['payment_value'].sum()
    total_customers = df['customer_unique_id'].nunique()
    avg_order_val  = total_revenue / total_orders if total_orders > 0 else 0
    avg_review     = df['review_score'].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, value, fmt in zip(
        [c1, c2, c3, c4, c5],
        ["Total Pesanan", "Total Pendapatan", "Pelanggan Unik", "Rata-rata Order", "Avg Review"],
        [total_orders, total_revenue, total_customers, avg_order_val, avg_review],
        ["{:,}", "R${:,.0f}", "{:,}", "R${:,.0f}", "{:.2f} ⭐"]
    ):
        col.markdown(f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{fmt.format(value)}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Tren Pesanan & Pendapatan Bulanan</div>', unsafe_allow_html=True)

    monthly = df.groupby('order_year_month').agg(
        total_orders=('order_id', 'nunique'),
        total_revenue=('payment_value', 'sum')
    ).reset_index()
    monthly['order_year_month'] = monthly['order_year_month'].astype(str)

    fig, axes = plt.subplots(2, 1, figsize=(14, 8), facecolor='white')
    for ax, col, color, label in zip(
        axes,
        ['total_orders', 'total_revenue'],
        ['#38bdf8', '#4ade80'],
        ['Jumlah Pesanan', 'Pendapatan (BRL)']
    ):
        ax.plot(monthly['order_year_month'], monthly[col],
                color=color, linewidth=2.5, marker='o', markersize=4)
        ax.fill_between(monthly['order_year_month'], monthly[col], alpha=0.15, color=color)
        ax.set_ylabel(label, fontsize=11)
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='y', alpha=0.3)

    axes[0].set_title('Jumlah Pesanan per Bulan', fontsize=13, fontweight='bold')
    axes[1].set_title('Pendapatan per Bulan', fontsize=13, fontweight='bold')
    axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'R${x/1e6:.1f}M'))

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ── HALAMAN: Produk & Kategori ───────────────────────────────────────────────
elif page == "🏷️ Produk & Kategori":
    st.title("🏷️ Produk & Kategori")

    if not data_loaded:
        st.stop()

    n_top = st.slider("Tampilkan Top N Kategori:", 5, 20, 10)

    col1, col2 = st.columns(2)

    top_qty = df.groupby('product_category_name_english')['order_id'] \
        .count().nlargest(n_top).reset_index()
    top_qty.columns = ['category', 'total_items']

    top_rev = df.groupby('product_category_name_english')['price'] \
        .sum().nlargest(n_top).reset_index()
    top_rev.columns = ['category', 'total_revenue']

    with col1:
        st.markdown(f"**Top {n_top} — Jumlah Item Terjual**")
        fig, ax = plt.subplots(figsize=(7, 6), facecolor='white')
        ax.barh(top_qty['category'], top_qty['total_items'],
                color=sns.color_palette('Blues_r', n_top))
        ax.invert_yaxis()
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.markdown(f"**Top {n_top} — Total Pendapatan (BRL)**")
        fig, ax = plt.subplots(figsize=(7, 6), facecolor='white')
        ax.barh(top_rev['category'], top_rev['total_revenue'],
                color=sns.color_palette('Greens_r', n_top))
        ax.invert_yaxis()
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'R${x/1e6:.1f}M'))
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

# ── HALAMAN: Ulasan ──────────────────────────────────────────────────────────
elif page == "⭐ Ulasan Pelanggan":
    st.title("⭐ Analisis Ulasan Pelanggan")

    if not data_loaded:
        st.stop()

    review_counts = df['review_score'].value_counts().sort_index().reset_index()
    review_counts.columns = ['score', 'count']

    colors_r = ['#ef5350','#ff7043','#ffca28','#66bb6a','#42a5f5']

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Distribusi Review Score**")
        fig, ax = plt.subplots(figsize=(7, 5), facecolor='white')
        bars = ax.bar(review_counts['score'], review_counts['count'],
                      color=colors_r, edgecolor='white')
        for bar, cnt in zip(bars, review_counts['count']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                    f'{cnt:,}', ha='center', fontsize=10)
        ax.set_xlabel('Review Score')
        ax.set_ylabel('Jumlah')
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.markdown("**Proporsi Review Score**")
        fig, ax = plt.subplots(figsize=(7, 5), facecolor='white')
        ax.pie(review_counts['count'],
               labels=[f'⭐ {s}' for s in review_counts['score']],
               colors=colors_r, autopct='%1.1f%%', startangle=140,
               wedgeprops={'edgecolor':'white','linewidth':2})
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("---")
    st.markdown("**Review Score berdasarkan Kategori Produk (Top 10)**")
    top10_cats = df['product_category_name_english'].value_counts().head(10).index
    review_by_cat = df[df['product_category_name_english'].isin(top10_cats)] \
        .groupby('product_category_name_english')['review_score'].mean() \
        .sort_values(ascending=False).reset_index()

    fig, ax = plt.subplots(figsize=(12, 5), facecolor='white')
    bars = ax.barh(review_by_cat['product_category_name_english'],
                   review_by_cat['review_score'],
                   color=sns.color_palette('RdYlGn', 10))
    ax.set_xlim(1, 5)
    ax.axvline(x=4, color='#94a3b8', linestyle='--', alpha=0.5, label='Skor 4')
    ax.invert_yaxis()
    ax.set_xlabel('Rata-rata Review Score')
    ax.spines[['top','right']].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ── HALAMAN: Pembayaran ──────────────────────────────────────────────────────
elif page == "💳 Pembayaran":
    st.title("💳 Analisis Metode Pembayaran")

    if not data_loaded:
        st.stop()

    pay_sum = payments_df.groupby('payment_type').agg(
        jumlah=('order_id', 'count'),
        total=('payment_value', 'sum')
    ).reset_index().sort_values('jumlah', ascending=False)

    col1, col2 = st.columns(2)
    pal = sns.color_palette('Set2', len(pay_sum))

    with col1:
        st.markdown("**Jumlah Transaksi**")
        fig, ax = plt.subplots(figsize=(6, 5), facecolor='white')
        ax.bar(pay_sum['payment_type'], pay_sum['jumlah'], color=pal)
        ax.spines[['top','right']].set_visible(False)
        plt.xticks(rotation=20)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.markdown("**Total Nilai Pembayaran (BRL)**")
        fig, ax = plt.subplots(figsize=(6, 5), facecolor='white')
        ax.bar(pay_sum['payment_type'], pay_sum['total'], color=pal)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'R${x/1e6:.0f}M'))
        ax.spines[['top','right']].set_visible(False)
        plt.xticks(rotation=20)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("---")
    st.markdown("**Distribusi Nilai Cicilan Kartu Kredit**")
    cc_install = payments_df[payments_df['payment_type'] == 'credit_card']
    install_counts = cc_install['payment_installments'].value_counts().sort_index().head(12)
    fig, ax = plt.subplots(figsize=(12, 4), facecolor='white')
    ax.bar(install_counts.index, install_counts.values, color='#38bdf8')
    ax.set_xlabel('Jumlah Cicilan')
    ax.set_ylabel('Jumlah Transaksi')
    ax.spines[['top','right']].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ── HALAMAN: RFM ─────────────────────────────────────────────────────────────
elif page == "👥 RFM Analysis":
    st.title("👥 RFM Analysis — Segmentasi Pelanggan")
    st.info("RFM Analysis mengelompokkan pelanggan berdasarkan **Recency** (kebaruan), **Frequency** (frekuensi), dan **Monetary** (nilai transaksi).")

    if not data_loaded:
        st.stop()

    ref_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

    rfm = df.groupby('customer_unique_id').agg(
        Recency   = ('order_purchase_timestamp', lambda x: (ref_date - x.max()).days),
        Frequency = ('order_id', 'nunique'),
        Monetary  = ('payment_value', 'sum')
    ).reset_index()

    rfm['R_score'] = pd.qcut(rfm['Recency'],   q=5, labels=[5,4,3,2,1], duplicates='drop')
    rfm['F_score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=5, labels=[1,2,3,4,5])
    rfm['M_score'] = pd.qcut(rfm['Monetary'],  q=5, labels=[1,2,3,4,5], duplicates='drop')
    rfm['RFM_Total'] = rfm[['R_score','F_score','M_score']].astype(int).sum(axis=1)

    def segment(row):
        r,f,m = int(row['R_score']),int(row['F_score']),int(row['M_score'])
        if r>=4 and f>=4 and m>=4:   return 'Champions'
        elif r>=3 and f>=3:           return 'Loyal Customers'
        elif r>=4 and f<=2:           return 'Recent Customers'
        elif r>=3 and f<=2 and m>=3:  return 'Potential Loyalists'
        elif r<=2 and f>=3:           return 'At Risk'
        elif r==1 and f>=4:           return 'Cant Lose Them'
        elif r<=2 and f<=2:           return 'Lost Customers'
        else:                         return 'Need Attention'

    rfm['Segment'] = rfm.apply(segment, axis=1)
    seg_sum = rfm['Segment'].value_counts().reset_index()
    seg_sum.columns = ['Segment', 'Count']

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Distribusi Segmen**")
        fig, ax = plt.subplots(figsize=(7, 5), facecolor='white')
        pal_s = sns.color_palette('tab10', len(seg_sum))
        ax.barh(seg_sum['Segment'], seg_sum['Count'], color=pal_s)
        ax.invert_yaxis()
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.markdown("**Scatter: Recency vs Monetary**")
        fig, ax = plt.subplots(figsize=(7, 5), facecolor='white')
        sc = ax.scatter(rfm['Recency'], rfm['Monetary'],
                        c=rfm['RFM_Total'], cmap='RdYlGn', alpha=0.5, s=8)
        plt.colorbar(sc, ax=ax, label='RFM Score')
        ax.set_xlabel('Recency (hari)')
        ax.set_ylabel('Monetary (BRL)')
        ax.set_yscale('log')
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("**Rata-rata RFM per Segmen**")
    rfm_table = rfm.groupby('Segment')[['Recency','Frequency','Monetary']].mean().round(2)
    st.dataframe(rfm_table.style.background_gradient(cmap='Blues', subset=['Monetary']), use_container_width=True)

# ── HALAMAN: Geospatial ──────────────────────────────────────────────────────
elif page == "🗺️ Geospatial":
    st.title("🗺️ Geospatial Analysis — Distribusi Geografis")
    st.info("Analisis distribusi pelanggan dan penjual berdasarkan lokasi geografis di Brasil.")

    if not data_loaded:
        st.stop()

    view = st.radio("Tampilkan:", ["Distribusi Pelanggan", "Distribusi Penjual", "Pesanan per State"])

    geo_dedup = geo_df.drop_duplicates('geolocation_zip_code_prefix')

    if view == "Distribusi Pelanggan":
        merged = customers_df.merge(
            geo_dedup[['geolocation_zip_code_prefix','geolocation_lat','geolocation_lng']],
            left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix', how='inner'
        ).dropna(subset=['geolocation_lat','geolocation_lng'])
        locs = merged[['geolocation_lat','geolocation_lng']].values.tolist()
        m = folium.Map(location=[-15.0, -51.0], zoom_start=4, tiles='CartoDB positron')
        HeatMap(locs, radius=8, blur=10, min_opacity=0.3).add_to(m)
        st.markdown("**Heatmap Distribusi Pelanggan**")
        st_folium(m, width=900, height=500)

    elif view == "Distribusi Penjual":
        merged = sellers_df.merge(
            geo_dedup[['geolocation_zip_code_prefix','geolocation_lat','geolocation_lng']],
            left_on='seller_zip_code_prefix', right_on='geolocation_zip_code_prefix', how='inner'
        ).dropna(subset=['geolocation_lat','geolocation_lng'])
        locs = merged[['geolocation_lat','geolocation_lng']].values.tolist()
        m = folium.Map(location=[-15.0, -51.0], zoom_start=4, tiles='CartoDB positron')
        HeatMap(locs, radius=10, blur=12, min_opacity=0.3,
                gradient={0.2:'blue', 0.5:'lime', 1.0:'red'}).add_to(m)
        st.markdown("**Heatmap Distribusi Penjual**")
        st_folium(m, width=900, height=500)

    else:
        state_ord = df.groupby('customer_state').agg(
            total_orders=('order_id','nunique'),
            total_revenue=('payment_value','sum')
        ).reset_index().sort_values('total_orders', ascending=False)

        fig, ax = plt.subplots(figsize=(14, 5), facecolor='white')
        ax.bar(state_ord['customer_state'], state_ord['total_orders'],
               color=sns.color_palette('YlOrRd_r', len(state_ord)))
        ax.set_xlabel('State')
        ax.set_ylabel('Jumlah Pesanan')
        ax.set_title('Distribusi Pesanan per Negara Bagian', fontsize=13, fontweight='bold')
        ax.tick_params(axis='x', rotation=45)
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

        st.dataframe(state_ord.rename(columns={
            'customer_state':'State',
            'total_orders':'Jumlah Pesanan',
            'total_revenue':'Total Pendapatan (BRL)'
        }), use_container_width=True)

# ── HALAMAN: Clustering ──────────────────────────────────────────────────────
elif page == "🔵 Clustering":
    st.title("🔵 Clustering Pelanggan — Binning")
    st.info("Pengelompokan pelanggan berdasarkan total spending dan keaktifan (recency) menggunakan teknik binning.")

    if not data_loaded:
        st.stop()

    ref_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    rfm2 = df.groupby('customer_unique_id').agg(
        Recency  = ('order_purchase_timestamp', lambda x: (ref_date - x.max()).days),
        Monetary = ('payment_value', 'sum')
    ).reset_index()

    rfm2['Spending_Cluster'] = pd.cut(
        rfm2['Monetary'],
        bins=[0,100,300,600,1500,rfm2['Monetary'].max()+1],
        labels=['Bronze\n(<R$100)','Silver\n(R$100-300)','Gold\n(R$300-600)',
                'Platinum\n(R$600-1500)','Diamond\n(>R$1500)'],
        right=True
    )
    rfm2['Recency_Cluster'] = pd.cut(
        rfm2['Recency'],
        bins=[0,30,90,180,365,rfm2['Recency'].max()+1],
        labels=['Very Active\n(≤30 hr)','Active\n(31-90 hr)',
                'Occasional\n(91-180 hr)','Dormant\n(181-365 hr)',
                'Churned\n(>365 hr)'],
        right=True
    )

    spend_sum  = rfm2['Spending_Cluster'].value_counts().sort_index().reset_index()
    recency_sum = rfm2['Recency_Cluster'].value_counts().sort_index().reset_index()

    col1, col2 = st.columns(2)
    colors_s = ['#CD7F32','#C0C0C0','#FFD700','#E5E4E2','#00C8FF']
    colors_r = ['#1a9641','#a6d96a','#ffffbf','#fdae61','#d7191c']

    with col1:
        st.markdown("**Clustering Berdasarkan Spending**")
        fig, ax = plt.subplots(figsize=(7, 5), facecolor='white')
        ax.bar(spend_sum['Spending_Cluster'].astype(str), spend_sum['count'],
               color=colors_s, edgecolor='white')
        ax.set_xlabel('Tier')
        ax.set_ylabel('Jumlah Pelanggan')
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.markdown("**Clustering Berdasarkan Recency**")
        fig, ax = plt.subplots(figsize=(7, 5), facecolor='white')
        ax.bar(recency_sum['Recency_Cluster'].astype(str), recency_sum['count'],
               color=colors_r, edgecolor='white')
        ax.set_xlabel('Tier')
        ax.set_ylabel('Jumlah Pelanggan')
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("**Statistik per Spending Cluster**")
    cluster_stats = rfm2.groupby('Spending_Cluster', observed=False)[['Recency','Monetary']].agg(['mean','median','count']).round(2)
    st.dataframe(cluster_stats, use_container_width=True)
