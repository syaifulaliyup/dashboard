import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Membaca dataset
file_path = 'main_data.csv'
main_data = pd.read_csv(file_path)

st.title('Dashboard E-Commerce')


st.header("Distribusi Metode Pembayaran Berdasarkan Jumlah Item dalam Pesanan")
# Menggabungkan data jumlah item per order dengan metode pembayaran
item_per_order = main_data.groupby("order_id")["order_item_id"].count().sort_values(ascending=False)
multiple_item_orders = item_per_order[item_per_order > 1]
order_payment_merged = main_data.groupby("order_id")["payment_type"].first().to_frame()
order_payment_merged["item_count"] = multiple_item_orders

# Membuat kategori jumlah item (>1 item saja)
order_payment_merged["item_category"] = pd.cut(order_payment_merged["item_count"], 
                                               bins=[1, 3, 5, 10, float("inf")], 
                                               labels=["2-3 items", "4-5 items", "6-10 items", "11+ items"])

# Menghitung jumlah pesanan berdasarkan metode pembayaran & jumlah item
payment_distribution = order_payment_merged.groupby(["item_category", "payment_type"]).size().unstack()

# Membuat plot Grouped Bar Chart
fig, ax = plt.subplots(figsize=(10, 6))
payment_distribution.plot(kind="bar", ax=ax, colormap="Set2")

ax.set_xlabel("Kategori Jumlah Item dalam Pesanan")
ax.set_ylabel("Jumlah Pesanan")
ax.set_title("")
ax.legend(title="Metode Pembayaran", bbox_to_anchor=(1.05, 1), loc="upper left")
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

# Menampilkan plot di Streamlit
st.pyplot(fig)

st.markdown("<br><br>", unsafe_allow_html=True)


#------------------------- Pertnyaan nomer 2-----------------------------
# Judul Aplikasi
st.header("Korelasi antara Jumlah Pelanggan di suatu Kota dengan Jumlah Pesanan pada Tahun 2018")

main_data["order_purchase_timestamp"] = pd.to_datetime(main_data["order_purchase_timestamp"])

# Filter hanya untuk tahun 2018
orders_2018 = main_data[main_data["order_purchase_timestamp"].dt.year == 2018]

# Hitung jumlah pelanggan unik per kota
customer_city_counts = main_data.groupby("customer_city")["customer_id"].nunique()

# Hitung jumlah pesanan per kota di tahun 2018
order_city_counts = orders_2018.groupby("customer_city")["order_id"].count()

# Gabungkan jumlah pelanggan dan jumlah pesanan
city_data = pd.DataFrame({"customer_count": customer_city_counts, "order_count": order_city_counts}).dropna()

# Menampilkan DataFrame di Streamlit
# Scatter Plot
fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(x=city_data["customer_count"], y=city_data["order_count"], alpha=0.7, color="royalblue", ax=ax)

ax.set_xlabel("Jumlah Pelanggan di Kota")
ax.set_ylabel("Jumlah Pesanan Tahun 2018")
ax.set_title("")
ax.grid(True)
# Tampilkan plot di Streamlit
st.pyplot(fig)
correlation_2018 = city_data.corr()
# Plot Heatmap
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(correlation_2018, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, ax=ax)
st.subheader('Heatmap')
ax.set_title("")
# Tampilkan Heatmap di Streamlit
st.pyplot(fig)

st.markdown("<br><br>", unsafe_allow_html=True)

# ------------------------------Pertnyaan nomer 3-----------------------------
# Pastikan kolom tanggal dalam format datetime
main_data["order_purchase_timestamp"] = pd.to_datetime(main_data["order_purchase_timestamp"])

# Filter untuk pesanan dalam 6 bulan terakhir
# Mendapatkan tanggal 6 bulan yang lalu menggunakan pd.Timestamp.today()
six_months_ago = main_data["order_purchase_timestamp"].max() - pd.DateOffset(months=6)
recent_orders = main_data[main_data["order_purchase_timestamp"] >= six_months_ago]

# Hitung total pendapatan per kategori produk
recent_orders["total_revenue"] = recent_orders["price"] * recent_orders["order_item_id"]

# Hitung total pendapatan per kategori produk
category_revenue = recent_orders.groupby("product_category_name_english")["total_revenue"].sum().sort_values(ascending=False)
category_revenue_top10 = category_revenue.head(10)

# Menampilkan DataFrame top 10 kategori produk berdasarkan pendapatan
st.header("Top 10 Kategori Produk Berdasarkan Pendapatan (6 Bulan Terakhir):")


# Visualisasi total pendapatan per kategori produk
fig, ax = plt.subplots(figsize=(10, 6))
category_revenue_top10.plot(kind="bar", color="skyblue", ax=ax)
ax.set_title("")
ax.set_xlabel("Kategori Produk")
ax.set_ylabel("Total Pendapatan")
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")

# Menampilkan bar chart di Streamlit
st.pyplot(fig)

# Ambil 3 kategori dengan pendapatan tertinggi

top_categories = category_revenue_top10.index[:3]

# Warna unik untuk setiap kategori
colors = sns.color_palette("Set2", len(top_categories))

# Buat figure dan axis untuk 3 subplot secara vertikal
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 12))

# Loop untuk setiap kategori
for i, category in enumerate(top_categories):
    # Filter data berdasarkan kategori produk
    category_df =main_data[main_data["product_category_name_english"] == category]

    # Gabungkan dengan dataset pembayaran
    # payment_data = category_df.merge(main_data, on="order_id")

    # Hitung jumlah pesanan berdasarkan metode pembayaran
    payment_type_distribution = main_data["payment_type"].value_counts().reset_index()
    payment_type_distribution.columns = ["payment_type", "total_orders"]

    # Buat barplot vertikal dengan seaborn
    sns.barplot(data=payment_type_distribution, x="payment_type", y="total_orders", 
                palette=[colors[i]] * len(payment_type_distribution), ax=ax[i])

    # Konfigurasi visualisasi
    ax[i].set_ylabel("Total Orders", fontsize=12)
    ax[i].set_xlabel("Payment Type", fontsize=12)
    ax[i].set_title(f"Metode Pembayaran - {category}", loc="center", fontsize=15)
    ax[i].tick_params(axis='x', rotation=45, labelsize=12)

# Tambahkan judul utama
st.subheader('Distribusi Metode Pembayaran untuk 3 Kategori Produk Teratas')
plt.suptitle("", fontsize=20)
plt.tight_layout()

# Menampilkan plot di Streamlit
st.pyplot(fig)

st.markdown("<br><br>", unsafe_allow_html=True)

# ------------------------------Pertnyaan nomer 4---------------------------------

# Resampling untuk menghitung total pesanan per tahun
years_orders_df = main_data.resample(rule='Y', on='order_purchase_timestamp').agg({
    "order_id": "count"
})

# Menambahkan nama kolom yang benar
years_orders_df.rename(columns={
    "order_id": "Total Orders"
}, inplace=True)

# Menambahkan kolom tahun dari index
years_orders_df.index = years_orders_df.index.year  
years_orders_df.reset_index(inplace=True)  
years_orders_df.rename(columns={
    "order_purchase_timestamp": "Tahun"  
}, inplace=True)

# Membuat plot
plt.figure(figsize=(10, 6))
sns.barplot(data=years_orders_df, x="Tahun", y="Total Orders", palette="viridis")

# Menambahkan judul dan label pada grafik
st.header('Total Orderan di Setiap Tahun')
plt.title("", fontsize=16)
plt.xlabel("Tahun", fontsize=12)
plt.ylabel("Total Orders", fontsize=12)

# Menampilkan nilai di atas setiap batang
for index, value in enumerate(years_orders_df["Total Orders"]):
    plt.text(index, value + 1000, str(value), ha='center', fontsize=10)

# Menampilkan grafik di Streamlit
st.pyplot(plt)

# Pengelompokkan data pada tahun 2016-2018

data_orders_2016 = main_data[main_data['order_purchase_timestamp'].dt.year == 2016]
data_orders_2017 = main_data[main_data['order_purchase_timestamp'].dt.year == 2017]
data_orders_2018 = main_data[main_data['order_purchase_timestamp'].dt.year == 2018]
# Pesanan 2016
orders_per_city_state_2016 = data_orders_2016.groupby(['customer_city', 'customer_state'])['order_id'].count().reset_index(name='total_orders')
orders_per_city_state_2016 = orders_per_city_state_2016.sort_values(by='total_orders', ascending=False)
orders_per_city_state_2016['city_state'] = orders_per_city_state_2016['customer_city'] + ', ' + orders_per_city_state_2016['customer_state']
# Ambil 10 besar kota/provinsi berdasarkan total orders
top_city_states_2016 = orders_per_city_state_2016.head(10)


# Pesanan 2017
orders_per_city_state_2017 = data_orders_2017.groupby(['customer_city', 'customer_state'])['order_id'].count().reset_index(name='total_orders')
orders_per_city_state_2017 = orders_per_city_state_2017.sort_values(by='total_orders', ascending=False)
orders_per_city_state_2017['city_state'] = orders_per_city_state_2017['customer_city'] + ', ' + orders_per_city_state_2017['customer_state']
# Ambil 10 besar kota/provinsi berdasarkan total orders
top_city_states_2017 = orders_per_city_state_2017.head(10)


# Pesanan 2018
orders_per_city_state_2018 = data_orders_2018.groupby(['customer_city', 'customer_state'])['order_id'].count().reset_index(name='total_orders')
orders_per_city_state_2018 = orders_per_city_state_2018.sort_values(by='total_orders', ascending=False)
# Gabungkan kolom 'customer_city' dan 'customer_state'
orders_per_city_state_2018['city_state'] = orders_per_city_state_2018['customer_city'] + ', ' + orders_per_city_state_2018['customer_state']
# Ambil 10 besar kota/provinsi berdasarkan total orders
top_city_states_2018 = orders_per_city_state_2018.head(10)


# Membuat figure dan axis untuk 3 subplot secara horizontal
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 8))
# Plot untuk tahun 2016
sns.barplot(data=top_city_states_2016, x='total_orders', y='city_state', palette='mako', ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Total Orders in 2016", loc="center", fontsize=15)
ax[0].tick_params(axis='x', labelsize=15)

# Plot untuk tahun 2017
sns.barplot(data=top_city_states_2017, x='total_orders', y='city_state', palette='mako', ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("Total Orders in 2017", loc="center", fontsize=15)
ax[1].tick_params(axis='x', labelsize=15)

# Plot untuk tahun 2018
sns.barplot(data=top_city_states_2018, x='total_orders', y='city_state', palette='mako', ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("Total Orders in 2018", loc="center", fontsize=15)
ax[2].tick_params(axis='x', labelsize=15)

# Menambahkan judul utama untuk seluruh grafik
st.subheader('Total Orderan Berdasarkan Kota/Negara Bagian Setiap Tahun')
plt.suptitle("", fontsize=20)

# Menampilkan grafik di Streamlit
st.pyplot(fig)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)


# -------------------------------Analisis Lanjutan--------------------------
st.header('Clustering Manual Grouping') 

#-------------------- Pengelompokkan Pertama-------------------
# Menghitung total pendapatan per pelanggan
main_data['total_transaction'] = main_data['payment_value'] + main_data['freight_value']
customer_revenue = main_data.groupby('customer_id')['total_transaction'].sum().reset_index()
customer_revenue.rename(columns={'total_transaction': 'total_revenue'}, inplace=True)
customer_revenue.sort_values(by="total_revenue", ascending=False, inplace=True)

# Fungsi untuk mengkategorikan pendapatan
def categorize_revenue(revenue):
    if revenue < 100:
        return 'Pendapatan Rendah'
    elif 100 <= revenue <= 500:
        return 'Pendapatan Menengah'
    else:
        return 'Pendapatan Tinggi'

# Menambahkan kategori pada data
customer_revenue['category'] = customer_revenue['total_revenue'].apply(categorize_revenue)

# Menyusun ringkasan jumlah pelanggan per kategori pendapatan
category_summary = customer_revenue.groupby('category')['customer_id'].count().reset_index()
category_summary.rename(columns={'customer_id': 'total_customers'}, inplace=True)

# Membuat visualisasi barplot
fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(data=category_summary, x='category', y='total_customers', palette='viridis', ax=ax)
ax.set_title('')
ax.set_xlabel('Kategori Pendapatan')
ax.set_ylabel('Jumlah Pelanggan')

# Menampilkan plot di Streamlit
st.subheader('Pengelompokan Pelanggan Berdasarkan Kategori Pendapatan')
st.pyplot(fig)



# -------------------------Pengelompokkan ke-2----------------------

# Fungsi untuk mengkategorikan harga produk
def categorize_price(row):
    if row["price"] < 100:
        return "Produk Murah"
    elif 100 <= row["price"] <= 500:
        return "Produk Menengah"
    elif row["price"] > 500:
        return "Produk Mahal"
    else:
        return "Tidak Terdefinisi"

# Menambahkan kolom kategori harga produk
main_data["product_price_category"] = main_data.apply(categorize_price, axis=1)

# Menghitung jumlah produk berdasarkan kategori harga
price_summary = main_data["product_price_category"].value_counts()

# Membuat visualisasi barplot
fig, ax = plt.subplots(figsize=(8, 6))
price_summary.plot(kind="bar", color=["blue", "orange", "green"], ax=ax)
ax.set_title("")
ax.set_xticklabels(price_summary.index, rotation=0)
ax.set_xlabel("Kategori Harga")
ax.set_ylabel("Jumlah Produk")

# Menampilkan plot di Streamlit
st.subheader('Pengelompokan Produk Berdasarkan Harga')
st.pyplot(fig)


# ------------------------Pengelompokkan ke-3--------------------------
# Hitung jumlah ulasan per kategori skor
review_summary = main_data['review_score'].value_counts().reset_index()
review_summary.columns = ['review_score', 'total_reviews']

# Tambahkan kategori berdasarkan review_score
def categorize_satisfaction(score):
    if score <= 2:
        return 'Tidak Puas'
    elif score == 3:
        return 'Netral'
    else:
        return 'Puas'

review_summary['satisfaction_category'] = review_summary['review_score'].apply(categorize_satisfaction)

# Agregasi data berdasarkan kategori kepuasan
category_summary = review_summary.groupby('satisfaction_category')['total_reviews'].sum().reset_index()

# Buat bar chart menggunakan Matplotlib
fig, ax = plt.subplots(figsize=(8, 6))
ax.bar(category_summary['satisfaction_category'], category_summary['total_reviews'], color=['red', 'orange', 'green'])

# Tambahkan judul dan label
ax.set_title('', fontsize=14)
ax.set_xlabel('Kategori Kepuasan', fontsize=12)
ax.set_ylabel('Jumlah Ulasan', fontsize=12)

# Tampilkan plot di Streamlit
st.subheader('Pengelompokan Pelanggan Pelanggan Berdasarkan Review Score')
st.pyplot(fig)


















