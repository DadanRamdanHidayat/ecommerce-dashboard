# 🛒 Proyek Analisis Data: E-Commerce Public Dataset

## Deskripsi Proyek

Proyek ini merupakan analisis data komprehensif terhadap **Brazilian E-Commerce Public Dataset** yang mencakup lebih dari 100.000 pesanan dari tahun 2016 hingga 2018. Analisis meliputi eksplorasi data, visualisasi, serta teknik analisis lanjutan seperti **RFM Analysis**, **Geospatial Analysis**, dan **Clustering/Binning**.

---

## Pertanyaan Bisnis yang Dijawab

1. Bagaimana tren jumlah pesanan dan pendapatan dari waktu ke waktu?
2. Kategori produk apa yang paling banyak terjual dan menghasilkan pendapatan tertinggi?
3. Bagaimana distribusi skor ulasan pelanggan?
4. Metode pembayaran apa yang paling banyak digunakan?
5. Siapa pelanggan terbaik berdasarkan RFM Analysis?
6. Bagaimana distribusi geografis pesanan dan penjual?
7. Bagaimana pengelompokan pelanggan berdasarkan nilai transaksi?

---

## Struktur Direktori

```
submission/
├── dashboard/
│   ├── main_data.csv          ← Dataset utama hasil data wrangling
│   └── dashboard.py           ← Script Streamlit untuk dashboard
├── data/
│   ├── customers_dataset.csv
│   ├── geolocation_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── products_dataset.csv
│   └── sellers_dataset.csv
├── notebook.ipynb             ← Jupyter Notebook analisis lengkap
├── README.md                  ← Dokumentasi proyek (file ini)
└── requirements.txt           ← Daftar library yang digunakan
```

---

## Cara Menjalankan Dashboard

### Prasyarat

Pastikan Python 3.9+ sudah terinstal di sistem Anda.

### Langkah 1 — Clone / Ekstrak Proyek

```bash
unzip submission.zip
cd submission
```

### Langkah 2 — Buat Virtual Environment (Opsional, Direkomendasikan)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Langkah 3 — Install Dependensi

```bash
pip install -r requirements.txt
```

### Langkah 4 — Jalankan Notebook (Opsional)

Sebelum menjalankan dashboard, jalankan dulu notebook untuk menghasilkan `dashboard/main_data.csv`:

```bash
jupyter notebook notebook.ipynb
```

Jalankan seluruh sel dari atas ke bawah. Pastikan ada langkah menyimpan master_df ke `dashboard/main_data.csv`:

```python
master_df.to_csv('dashboard/main_data.csv', index=False)
```

### Langkah 5 — Jalankan Dashboard Streamlit

```bash
streamlit run dashboard/dashboard.py
```

Dashboard akan terbuka secara otomatis di browser pada alamat:

```
http://localhost:8501
```

---

## Fitur Dashboard

| Halaman | Deskripsi |
|---|---|
| 📊 Overview | KPI utama, tren pesanan & pendapatan bulanan |
| 🏷️ Produk & Kategori | Top kategori berdasarkan volume & pendapatan |
| ⭐ Ulasan Pelanggan | Distribusi review score & perbandingan per kategori |
| 💳 Pembayaran | Analisis metode & cicilan pembayaran |
| 👥 RFM Analysis | Segmentasi pelanggan berdasarkan RFM |
| 🗺️ Geospatial | Heatmap distribusi pelanggan & penjual di Brasil |
| 🔵 Clustering | Pengelompokan pelanggan dengan binning |

---

## Teknik Analisis Lanjutan

### 1. RFM Analysis
Mengelompokkan pelanggan berdasarkan:
- **Recency**: Hari sejak transaksi terakhir
- **Frequency**: Jumlah transaksi unik
- **Monetary**: Total nilai pembelian

### 2. Geospatial Analysis
Menggunakan library `folium` untuk membuat heatmap interaktif distribusi pelanggan dan penjual di seluruh wilayah Brasil.

### 3. Clustering / Binning
Mengelompokkan pelanggan ke dalam tier spending (Bronze → Diamond) dan tier keaktifan (Very Active → Churned) menggunakan `pd.cut()`.

---

## Library Utama

- **pandas** — Manipulasi dan analisis data
- **numpy** — Komputasi numerik
- **matplotlib & seaborn** — Visualisasi data
- **folium & streamlit-folium** — Peta interaktif
- **streamlit** — Framework dashboard web

---

## Insight Utama

- Pertumbuhan pesanan signifikan pada 2017, terutama di bulan November (Black Friday).
- Kategori `bed_bath_table` dan `health_beauty` mendominasi penjualan.
- 57%+ pelanggan memberikan rating bintang 5.
- Kartu kredit adalah metode pembayaran paling populer.
- Konsentrasi pelanggan terbesar di São Paulo (SP).
- Mayoritas pelanggan hanya bertransaksi sekali — retensi menjadi tantangan utama.

---

*Dibuat dengan ❤️ menggunakan Python & Streamlit*
