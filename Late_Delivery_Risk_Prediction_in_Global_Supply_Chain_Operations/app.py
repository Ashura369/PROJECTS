import sys
import os
import streamlit as st
import pandas as pd
import numpy as np
import joblib

# Backward compatibility fix for scikit-learn unpickling version mismatch
import sklearn._loss.loss
sys.modules['_loss'] = sklearn._loss.loss

# Determine the absolute directory path of this script to handle paths dynamically on Streamlit Cloud
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, "late_delivery_model.pkl")
encoder_path = os.path.join(base_dir, "target_encoder.pkl")

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

# Cache Model & Encoder Loading
@st.cache_resource
def load_ml_objects():
    if not os.path.exists(model_path) or not os.path.exists(encoder_path):
        st.error("Saved model/encoder pickle files not found in the directory! Please run the notebook saving cell first.")
        return None, None
    model = joblib.load(model_path)
    encoder = joblib.load(encoder_path)
    return model, encoder

# Header
st.markdown("""
<div class="header-style">
    <h1>🚚 APL Logistics - Late Delivery Risk Predictor</h1>
    <p>Predict supply chain delivery status and identify potential delays using tuned machine learning models.</p>
</div>
""", unsafe_allow_html=True)

model, encoder = load_ml_objects()

if model is not None and encoder is not None:
    # Extract category choices dynamically from the loaded target encoder
    cat_cols = [
        'Payment Method', 'Delivery Status', 'Product Category', 'Customer City', 'Customer Country', 
        'Customer Segment', 'Customer State', 'Department Name', 'Market', 'Order City', 
        'Order Country', 'Order Region', 'Order State', 'Product Name', 'Shipping Mode'
    ]
    categories = {}
    for idx, col in enumerate(cat_cols):
        categories[col] = sorted(list(encoder.categories_[idx]))

    st.sidebar.header("Navigation & Options")
    st.sidebar.info("Fill out the order and shipment details across the tabs, then click 'Predict Delivery Risk' at the bottom.")

    # Grouping inputs into 4 logical tabs
    tab_ship, tab_prod, tab_cust, tab_dest = st.tabs([
        "📦 Shipment & Order Basics", 
        "🏷️ Product & Financials", 
        "👤 Customer Demographics", 
        "📍 Order Destination"
    ])

    with tab_ship:
        st.subheader("Shipment and Order Basics")
        col1, col2 = st.columns(2)
        with col1:
            payment_method = st.selectbox(
                'Payment Method', 
                options=categories['Payment Method']
            )
            delivery_status = st.selectbox(
                'Delivery Status', 
                options=categories['Delivery Status'],
                help="Warning: If keeping this in active features, it serves as a strong predictor."
            )
        with col2:
            shipping_mode = st.selectbox(
                'Shipping Mode', 
                options=categories['Shipping Mode']
            )
            days_shipment = st.slider(
                'Days for shipment (scheduled)', 
                min_value=0, 
                max_value=10, 
                value=3
            )

    with tab_prod:
        st.subheader("Product & Financial Details")
        col1, col2 = st.columns(2)
        with col1:
            product_category = st.selectbox(
                'Product Category', 
                options=categories['Product Category']
            )
            product_name = st.selectbox(
                'Product Name', 
                options=categories['Product Name']
            )
            dept_name = st.selectbox(
                'Department Name', 
                options=categories['Department Name']
            )
            product_price = st.number_input(
                'Product Price ($)', 
                min_value=0.0, 
                value=120.0
            )
            quantity = st.slider(
                'Order Item Quantity', 
                min_value=1, 
                max_value=20, 
                value=1
            )
        with col2:
            total_sales = st.number_input(
                'Total Sales ($)', 
                min_value=0.0, 
                value=150.0
            )
            price_discount = st.number_input(
                'Price After Discount ($)', 
                min_value=0.0, 
                value=130.0
            )
            discount = st.number_input(
                'Order Item Discount ($)', 
                min_value=0.0, 
                value=20.0
            )
            discount_rate = st.slider(
                'Order Item Discount Rate', 
                min_value=0.0, 
                max_value=1.0, 
                value=0.1
            )
            profit_ratio = st.number_input(
                'Order Item Profit Ratio', 
                value=0.2
            )

    with tab_cust:
        st.subheader("Customer Demographics")
        col1, col2 = st.columns(2)
        with col1:
            cust_country = st.selectbox(
                'Customer Country', 
                options=categories['Customer Country']
            )
            cust_state = st.selectbox(
                'Customer State', 
                options=categories['Customer State']
            )
            cust_city = st.selectbox(
                'Customer City', 
                options=categories['Customer City']
            )
        with col2:
            cust_segment = st.selectbox(
                'Customer Segment', 
                options=categories['Customer Segment']
            )
            cust_zipcode = st.number_input(
                'Customer Zipcode', 
                value=72501.0
            )
            latitude = st.number_input(
                'Latitude', 
                value=18.2
            )
            longitude = st.number_input(
                'Longitude', 
                value=-66.0
            )

    with tab_dest:
        st.subheader("Order Destination details")
        col1, col2 = st.columns(2)
        with col1:
            order_market = st.selectbox(
                'Market', 
                options=categories['Market']
            )
            order_country = st.selectbox(
                'Order Country', 
                options=categories['Order Country']
            )
            order_region = st.selectbox(
                'Order Region', 
                options=categories['Order Region']
            )
        with col2:
            order_state = st.selectbox(
                'Order State', 
                options=categories['Order State']
            )
            order_city = st.selectbox(
                'Order City', 
                options=categories['Order City']
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
                st.success(f"✅ **Low Late Delivery Risk.**")
                st.write(f"The model predicts a **{pred_prob * 100:.2f}%** probability of delay (highly likely to deliver on time).")
                
        except Exception as e:
            st.error(f"An error occurred during model prediction: {str(e)}")
            st.info("Ensure the Python packages and scikit-learn models are compatible with version changes.")
else:
    st.warning("Please ensure the model pickle files are properly populated before predicting.")
