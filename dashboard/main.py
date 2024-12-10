import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Default paths for datasets
default_paths = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
}

try:
    # Read datasets
    customers_df = pd.read_csv(default_paths["customers"])
    orders_df = pd.read_csv(default_paths["orders"])
    products_df = pd.read_csv(default_paths["products"])
    order_items_df = pd.read_csv(default_paths["order_items"])

    st.success("All datasets successfully loaded!")

    # Data preprocessing
    all_df = pd.merge(orders_df, customers_df, on="customer_id", how="left")
    all_df = pd.merge(all_df, order_items_df, on="order_id", how="left")
    all_df = pd.merge(all_df, products_df, on="product_id", how="left")

    all_df['order_approved_at'] = pd.to_datetime(all_df['order_approved_at'], errors="coerce")
    all_df['Month'] = all_df['order_approved_at'].dt.to_period('M').astype(str)
    all_df.sort_values(by="order_approved_at", inplace=True)
    all_df.reset_index(inplace=True, drop=True)

    # Sidebar: Select date range
    min_date = all_df["order_approved_at"].min()
    max_date = all_df["order_approved_at"].max()

    with st.sidebar:
        st.image("logo.webp", width=100)
        start_date, end_date = st.date_input(
            label="Select Date Range",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )

    # Filter data by date range
    filtered_data = all_df[(all_df["order_approved_at"] >= str(start_date)) &
                           (all_df["order_approved_at"] <= str(end_date))]

    # Question 1: Top 10 most purchased product categories (Descending)
    st.markdown("### 1. Kategori Produk yang Paling Sering Dibeli (Descending)")

    # Hitung jumlah pembelian berdasarkan kategori produk
    top_categories = (
        filtered_data['product_category_name']
        .value_counts()
        .head(10)
        .sort_values(ascending=False)
    )

    # Konversi ke DataFrame untuk visualisasi
    top_categories_df = pd.DataFrame({
        "Kategori Produk": top_categories.index,
        "Jumlah Pembelian": top_categories.values
    })

    # Visualisasi dengan Matplotlib
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x=top_categories_df["Kategori Produk"],
        y=top_categories_df["Jumlah Pembelian"],
        palette="viridis",
        ax=ax
    )
    ax.set_title("Top 10 Kategori Produk yang Sering Dibeli", fontsize=16)
    ax.set_xlabel("Kategori Produk", fontsize=12)
    ax.set_ylabel("Jumlah Pembelian", fontsize=12)
    ax.tick_params(axis='x', rotation=45)

    # Tampilkan grafik dan tabel
    st.pyplot(fig)
    st.write("**Top 10 Kategori Produk yang Sering Dibeli:**")
    st.table(top_categories_df)

    # Question 2: Number of orders per month and trend
    st.markdown("### 2. Jumlah Pesanan per Bulan (Visual Style Mirip Gambar)")

    # Hitung jumlah pesanan per bulan
    orders_per_month = filtered_data.groupby('Month').size()

    # Plot menggunakan Matplotlib
    plt.figure(figsize=(12, 6))
    orders_per_month.plot(kind="line", marker='o', linestyle='--', color='b')
    plt.title("Tren Jumlah Pesanan per Bulan", fontsize=16)
    plt.xlabel("Bulan-Tahun", fontsize=12)
    plt.ylabel("Jumlah Pesanan", fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    # Tampilkan grafik di Streamlit
    st.pyplot(plt)

    # Trend analysis
    st.markdown("#### Analisis Tren")
    if len(orders_per_month) > 1:
        trend_slope = (orders_per_month.iloc[-1] - orders_per_month.iloc[0]) / len(orders_per_month)
        trend = "meningkat" if trend_slope > 0 else "menurun" if trend_slope < 0 else "stabil"
        st.write(f"Tren pesanan per bulan cenderung **{trend}**.")
    else:
        st.write("Data tidak cukup untuk menganalisis tren.")

    # Question 3: New vs Existing customers
    st.markdown("### 3. New Customer vs Existing Customer")

    customer_counts = filtered_data['customer_id'].value_counts()
    customer_types = pd.DataFrame({
        'Customer Type': ['New', 'Existing'],
        'Count': [customer_counts[customer_counts == 1].count(),
                  customer_counts[customer_counts > 1].count()]
    })

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(customer_types['Customer Type'], customer_types['Count'], color=['orange', 'blue'])
    ax.set_title("New vs Existing Customers", fontsize=16)
    ax.set_ylabel("Count", fontsize=12)
    st.pyplot(fig)

    st.write("**Summary:**")
    st.table(customer_types)

except Exception as e:
    st.error(f"Error processing data: {e}")
