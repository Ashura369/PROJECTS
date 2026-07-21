import sys
import os
import streamlit as st
import pandas as pd
import numpy as np
import joblib

# Backward compatibility fix for scikit-learn unpickling version mismatch
import sklearn._loss.loss
sys.modules['_loss'] = sklearn._loss.loss

# Set page configuration with a premium look
st.set_page_config(
    page_title="APL Logistics - Late Delivery Prediction",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling for premium design
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #0c2340;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        border: none;
        padding: 0.5rem 2rem;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #1d3557;
        color: white;
    }
    .header-style {
        background-color: #0c2340;
        padding: 2rem;
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# 1. Cache Dataset Loading
@st.cache_data
def load_data():
    csv_path = "dataset/APL_Logistics.csv"
    if not os.path.exists(csv_path):
        st.error(f"Dataset not found at {csv_path}. Please check the folder structure.")
        return None
    df = pd.read_csv(csv_path, encoding='latin1')
    # Apply column name mappings used in the notebook
    df = df.rename(columns={
        'Type': 'Payment Method',
        'Late_delivery_risk': 'Late Delivery ?',
        'Category Name': 'Product Category',
        'Sales': 'Total Sales',
        'Order Item Total': 'Price After Discount'
    })
    return df

# 2. Cache Model & Encoder Loading
@st.cache_resource
def load_ml_objects():
    model_path = 'late_delivery_model.pkl'
    encoder_path = 'target_encoder.pkl'
    if not os.path.exists(model_path) or not os.path.exists(encoder_path):
        st.error("Saved model/encoder pickle files not found in the directory! Please run the notebook saving cell first.")
        return None, None
    model = joblib.load(model_path)
    encoder = joblib.load(encoder_path)
    return model, encoder

# Header
st.markdown("""
<div class="header-style">
    <h1>APL Logistics - Late Delivery Risk Predictor</h1>
    <p>Predict supply chain delivery status and identify potential delays using tuned machine learning models.</p>
</div>
""", unsafe_allow_html=True)

df = load_data()
model, encoder = load_ml_objects()

if df is not None and model is not None and encoder is not None:
    st.sidebar.header("Navigation & Options")
    st.sidebar.info("Fill out the order and shipment details across the tabs, then click 'Predict Delivery Risk' at the bottom.")

    # Grouping inputs into 4 logical tabs
    tab_ship, tab_prod, tab_cust, tab_dest = st.tabs([
        "Shipment & Order Basics", 
        "Product & Financials", 
        "Customer Demographics", 
        "Order Destination"
    ])

    with tab_ship:
        st.subheader("Shipment and Order Basics")
        col1, col2 = st.columns(2)
        with col1:
            payment_method = st.selectbox(
                'Payment Method', 
                options=sorted(df['Payment Method'].unique())
            )
            delivery_status = st.selectbox(
                'Delivery Status', 
                options=sorted(df['Delivery Status'].unique()),
                help="Warning: If keeping this in active features, it serves as a strong predictor."
            )
        with col2:
            shipping_mode = st.selectbox(
                'Shipping Mode', 
                options=sorted(df['Shipping Mode'].unique())
            )
            days_shipment = st.slider(
                'Days for shipment (scheduled)', 
                min_value=0, 
                max_value=10, 
                value=int(df['Days for shipment (scheduled)'].median())
            )

    with tab_prod:
        st.subheader("Product & Financial Details")
        col1, col2 = st.columns(2)
        with col1:
            product_category = st.selectbox(
                'Product Category', 
                options=sorted(df['Product Category'].unique())
            )
            # Dynamically filter product names based on selected category
            filtered_products = df[df['Product Category'] == product_category]['Product Name'].unique()
            product_name = st.selectbox(
                'Product Name', 
                options=sorted(filtered_products)
            )
            dept_name = st.selectbox(
                'Department Name', 
                options=sorted(df['Department Name'].unique())
            )
            product_price = st.number_input(
                'Product Price ($)', 
                min_value=0.0, 
                value=float(df['Product Price'].mean())
            )
            quantity = st.slider(
                'Order Item Quantity', 
                min_value=1, 
                max_value=20, 
                value=int(df['Order Item Quantity'].median())
            )
        with col2:
            total_sales = st.number_input(
                'Total Sales ($)', 
                min_value=0.0, 
                value=float(df['Total Sales'].mean())
            )
            price_discount = st.number_input(
                'Price After Discount ($)', 
                min_value=0.0, 
                value=float(df['Price After Discount'].mean())
            )
            discount = st.number_input(
                'Order Item Discount ($)', 
                min_value=0.0, 
                value=float(df['Order Item Discount'].mean())
            )
            discount_rate = st.slider(
                'Order Item Discount Rate', 
                min_value=0.0, 
                max_value=1.0, 
                value=float(df['Order Item Discount Rate'].mean())
            )
            profit_ratio = st.number_input(
                'Order Item Profit Ratio', 
                value=float(df['Order Item Profit Ratio'].mean())
            )

    with tab_cust:
        st.subheader("Customer Demographics")
        col1, col2 = st.columns(2)
        with col1:
            cust_country = st.selectbox(
                'Customer Country', 
                options=sorted(df['Customer Country'].unique())
            )
            # Dynamically filter customer states based on selected country
            cust_states = df[df['Customer Country'] == cust_country]['Customer State'].unique()
            cust_state = st.selectbox(
                'Customer State', 
                options=sorted(cust_states)
            )
            # Dynamically filter customer cities based on selected state
            cust_cities = df[df['Customer State'] == cust_state]['Customer City'].unique()
            cust_city = st.selectbox(
                'Customer City', 
                options=sorted(cust_cities)
            )
        with col2:
            cust_segment = st.selectbox(
                'Customer Segment', 
                options=sorted(df['Customer Segment'].unique())
            )
            cust_zipcode = st.number_input(
                'Customer Zipcode', 
                value=float(df['Customer Zipcode'].median() or 0.0)
            )
            latitude = st.number_input(
                'Latitude', 
                value=float(df['Latitude'].mean())
            )
            longitude = st.number_input(
                'Longitude', 
                value=float(df['Longitude'].mean())
            )

    with tab_dest:
        st.subheader("Order Destination details")
        col1, col2 = st.columns(2)
        with col1:
            order_market = st.selectbox(
                'Market', 
                options=sorted(df['Market'].unique())
            )
            # Dynamically filter order countries based on selected market
            order_countries = df[df['Market'] == order_market]['Order Country'].unique()
            order_country = st.selectbox(
                'Order Country', 
                options=sorted(order_countries)
            )
            # Dynamically filter order regions based on selected country
            order_regions = df[df['Order Country'] == order_country]['Order Region'].unique()
            order_region = st.selectbox(
                'Order Region', 
                options=sorted(order_regions)
            )
        with col2:
            # Dynamically filter order states based on selected country
            order_states = df[df['Order Country'] == order_country]['Order State'].unique()
            order_state = st.selectbox(
                'Order State', 
                options=sorted(order_states)
            )
            # Dynamically filter order cities based on selected state
            order_cities = df[df['Order State'] == order_state]['Order City'].unique()
            order_city = st.selectbox(
                'Order City', 
                options=sorted(order_cities)
            )

    # 3. Assemble and Predict
    st.markdown("---")
    if st.button("Predict Delivery Risk"):
        # Assemble input dictionary
        input_data = {
            'Payment Method': payment_method,
            'Days for shipment (scheduled)': days_shipment,
            'Delivery Status': delivery_status,
            'Product Category': product_category,
            'Customer City': cust_city,
            'Customer Country': cust_country,
            'Customer Segment': cust_segment,
            'Customer State': cust_state,
            'Customer Zipcode': cust_zipcode,
            'Department Name': dept_name,
            'Latitude': latitude,
            'Longitude': longitude,
            'Market': order_market,
            'Order City': order_city,
            'Order Country': order_country,
            'Order Item Discount': discount,
            'Order Item Discount Rate': discount_rate,
            'Order Item Profit Ratio': profit_ratio,
            'Order Item Quantity': quantity,
            'Total Sales': total_sales,
            'Price After Discount': price_discount,
            'Order Region': order_region,
            'Order State': order_state,
            'Product Name': product_name,
            'Product Price': product_price,
            'Shipping Mode': shipping_mode
        }

        # Convert to DataFrame
        input_df = pd.DataFrame([input_data])
        
        # Ensure column order matches feature_names_in_ exactly
        features_list = list(model.feature_names_in_)
        input_df = input_df[features_list]

        # Target encode categorical columns
        cat_cols = [
            'Payment Method', 'Delivery Status', 'Product Category', 'Customer City', 'Customer Country', 
            'Customer Segment', 'Customer State', 'Department Name', 'Market', 'Order City', 
            'Order Country', 'Order Region', 'Order State', 'Product Name', 'Shipping Mode'
        ]
        
        input_df_encoded = input_df.copy()
        input_df_encoded[cat_cols] = encoder.transform(input_df[cat_cols])

        # Make prediction
        try:
            pred_prob = model.predict_proba(input_df_encoded)[0, 1]
            pred_class = model.predict(input_df_encoded)[0]

            # Results UI
            st.markdown("### Prediction Outcome")
            if pred_class == 1:
                st.error(f"⚠️ **High Late Delivery Risk Detected!**")
                st.write(f"The model predicts a **{pred_prob * 100:.2f}%** probability that this shipment will be delayed.")
            else:
                st.success(f"**Low Late Delivery Risk.**")
                st.write(f"The model predicts a **{pred_prob * 100:.2f}%** probability of delay (highly likely to deliver on time).")
                
        except Exception as e:
            st.error(f"An error occurred during model prediction: {str(e)}")
            st.info("Ensure the Python packages and scikit-learn models are compatible with version changes.")
else:
    st.warning("Please ensure the CSV dataset and model pickle files are properly populated before predicting.")
