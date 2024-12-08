import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

# Default paths for datasets
default_paths = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
}

try:
    # Read datasets directly from default paths
    customers_df = pd.read_csv(default_paths["customers"])
    orders_df = pd.read_csv(default_paths["orders"])
    products_df = pd.read_csv(default_paths["products"])
    order_items_df = pd.read_csv(default_paths["order_items"])

    st.success("All datasets successfully loaded!")

    # Data preprocessing
    datetime_cols = [
        "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"
    ]

    all_df = pd.merge(orders_df, customers_df, on="customer_id", how="left")
    all_df = pd.merge(all_df, order_items_df, on="order_id", how="left")
    all_df = pd.merge(all_df, products_df, on="product_id", how="left")

    for col in datetime_cols:
        if col in all_df.columns:
            all_df[col] = pd.to_datetime(all_df[col], errors="coerce")

    all_df.sort_values(by="order_approved_at", inplace=True)
    all_df.reset_index(inplace=True, drop=True)

    if not all_df.empty:
        min_date = all_df["order_approved_at"].min()
        max_date = all_df["order_approved_at"].max()

        # Sidebar
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

        # Add derived columns
        filtered_data['Month'] = filtered_data['order_approved_at'].dt.to_period('M')

        # Analysis and Visualizations
        st.markdown("### Analisis dan Visualisasi")

        # Question 1: Most frequently bought product
        st.markdown("## 1. Product yang paling sering dibeli")
        top_products = filtered_data['product_id'].value_counts().head(10)
        st.bar_chart(top_products)
        st.write(top_products)

        # Question 2: Number of orders per month and trend
        st.markdown("## 2. Jumlah pesanan per bulan")
        orders_per_month = filtered_data.groupby('Month').size()
        st.line_chart(orders_per_month)

        # Trend analysis
        st.markdown("### Trend Analysis")
        if len(orders_per_month) > 1:
            trend_slope = (orders_per_month.iloc[-1] - orders_per_month.iloc[0]) / len(orders_per_month)
            trend = "meningkat" if trend_slope > 0 else "menurun" if trend_slope < 0 else "stabil"
            st.write(f"Trend pesanan per bulan cenderung **{trend}**.")
        else:
            st.write("Data tidak cukup untuk menganalisis tren.")

        # Question 3: New vs Existing customers
        st.markdown("## 3. New Customer vs Existing Customer")
        customer_counts = filtered_data['customer_id'].value_counts()
        customer_types = pd.DataFrame({
            'type': ['New', 'Existing'],
            'count': [customer_counts[customer_counts == 1].count(),
                      customer_counts[customer_counts > 1].count()]
        })
        st.bar_chart(customer_types.set_index('type')['count'])
        st.write(customer_types)
except Exception as e:
    st.error(f"Error processing data: {e}")
