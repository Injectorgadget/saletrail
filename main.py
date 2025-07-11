# etsy_dashboard_app.py
# Streamlit-based Etsy Analytics Dashboard (CSV Upload)
import time

import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter

st.image("saletrail.png", width=300)

st.set_page_config(page_title="Etsy Analytics Dashboard", layout="wide")
#st.logo("saletrail.png", icon_image="saletrail.png", size="large")
st.title("Etsy Seller Dashboard")
st.markdown(
    """
Upload your exported CSV from Etsy to get insights into your shop's performance.
            
            
<style>
    .st-emotion-cache-auzihx 
    {
        height: 10rem;
        margin-left: 64px;
        margin-top: 32px;
        padding: 5%
        position: relative;
        }
</style>
        """,
    unsafe_allow_html=True

            )

# View switcher using tabs or radio buttons
view = st.radio("Choose a View", ["Order Summary", "Listing Summary"], horizontal=True)

if view == "Order Summary":
    uploaded_file = st.file_uploader("Upload your Etsy CSV (Orders)", type=["csv"], key="orders_upload")

    if uploaded_file:
        dfo = pd.read_csv(uploaded_file)
        st.subheader("Raw Data Preview")
        st.dataframe(dfo.head())

        if 'Sale Date' in dfo.columns:
            dfo['Sale Date'] = pd.to_datetime(dfo['Sale Date'])

            st.subheader("📦 Orders Over Time")
            orders_per_day = dfo.groupby(dfo['Sale Date'].dt.date).size().reset_index(name='Orders')
            fig1 = px.line(orders_per_day, x='Sale Date', y='Orders', title='Orders Per Day')
            st.plotly_chart(fig1, use_container_width=True)

            st.subheader("💰 Revenue Over Time")
            if 'Order Net' in dfo.columns:
                dfo['Order Net'] = dfo['Order Net'].replace('[\$,]', '', regex=True).astype(float)
                revenue_per_day = dfo.groupby(dfo['Sale Date'].dt.date)['Order Net'].sum().reset_index()
                fig2 = px.area(revenue_per_day, x='Sale Date', y='Order Net', title='Revenue Per Day')
                st.plotly_chart(fig2, use_container_width=True)

            st.subheader("🏆 Top Products")
            if 'Title' in dfo.columns:
                top_products = dfo['Title'].value_counts().head(10).reset_index()
                top_products.columns = ['Product', 'Orders']
                fig3 = px.bar(top_products, x='Orders', y='Product', orientation='h', title='Top 10 Products')
                st.plotly_chart(fig3, use_container_width=True)

        else:
            st.warning("This CSV doesn't contain order data.")

elif view == "Listing Summary":
    uploaded_file = st.file_uploader("Upload your Etsy CSV (Listings)", type=["csv"], key="listings_upload")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.subheader("Raw Data Preview")
        st.dataframe(df.head())

        if 'TAGS' in df.columns:
            st.subheader("🏷️ Tag Effectiveness")
            tag_counter = Counter()
            for tags in df['TAGS'].dropna():
                for tag in str(tags).split(','):
                    tag = tag.strip().lower()
                    if tag:
                        tag_counter[tag] += 1

            tag_df = pd.DataFrame(tag_counter.items(), columns=['Tag', 'Count'])
            tag_df = tag_df.sort_values(by='Count', ascending=False).head(20)
            fig4 = px.bar(tag_df, x='Count', y='Tag', orientation='h', title='Top 20 Tags Used')
            st.plotly_chart(fig4, use_container_width=True)


        # Low Inventory Highlight
            def highlight_row(row):
                if row['QUANTITY'] < int(user_input):
                    return ['background-color: #ffcccc'] * len(row)  # red
                elif row['QUANTITY'] > int(user_input):
                    return ['background-color: #9FE2BF'] * len(row)  # yellow
                else:
                    return [''] * len(row)

            if 'QUANTITY' in df.columns and 'TITLE' in df.columns:
                with st.form("my_submit_form"):
                    user_input = st.text_input("Low Tag Threshold: ")
                    submitted = st.form_submit_button("Submit")
                st.subheader("⚠️ Low Inventory Listings")
                low_inventory = df[['TITLE', 'QUANTITY']].copy()
                low_inventory['QUANTITY'] = pd.to_numeric(low_inventory['QUANTITY'], errors='coerce')

                styled_inventory = low_inventory.sort_values(by='QUANTITY').style.apply(highlight_row, axis=1)
                st.dataframe(styled_inventory, use_container_width=True)