import streamlit as st
import pandas as pd
import plotly.express as px
import os
import plotly.express as px

# Setting page config for a wider layout
st.set_page_config(page_title="Real Estate Buyer Segmentation", layout="wide")

st.title("Real Estate Buyer Segmentation Dashboard")
st.markdown("This dashboard provides live analytics on our machine learning buyer segmentation model.")

# Credits Section
st.markdown("""
    <div style='display: flex; justify-content: flex-end; align-items: center;'>
        <b style='margin-right: 15px; font-size: 16px;'>Credits : </b>
        <a href='https://github.com/pradhans369' target='_blank'>
            <img src='https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white' style='margin-right: 10px; border-radius: 8px;'>
        </a>
        <a href='https://www.linkedin.com/in/pradhans369/' target='_blank'>
            <img src='https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white' style='border-radius: 8px;'>
        </a>
    </div>
""", unsafe_allow_html=True)

# --- 1. DATA LOADING ---
@st.cache_data
def load_data():
    # Construct the absolute path based on the location of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'dataset', 'final_dataset.csv')
    
    # Read the lightning-fast CSV!
    df = pd.read_csv(file_path)
    
    # filtering out the unsold properties from the visualizations
    # analyzing only actual buyers!
    df = df[df['buyers_type'] != 'NO BUYERS']
    
    # Filling any empty values in categorical columns for cleaner filters
    df['country'] = df['country'].fillna('Unknown')
    df['region'] = df['region'].fillna('Unknown')
    df['acquisition_purpose'] = df['acquisition_purpose'].fillna('Unknown')
    df['client_type'] = df['client_type'].fillna('Unknown')
    
    return df

df = load_data()

# --- 2. SIDEBAR FILTERS ---
st.sidebar.header("User Controls")

# A helper function to create multi-selects with "All" option easily handled
def multiselect_filter(label, options):
    selected = st.sidebar.multiselect(label, options=options, default=options)
    return selected

countries = sorted(df['country'].unique())
selected_countries = multiselect_filter("Filter by Country", countries)

regions = sorted(df[df['country'].isin(selected_countries)]['region'].unique())
selected_regions = multiselect_filter("Filter by Region", regions)

purposes = sorted(df['acquisition_purpose'].unique())
selected_purposes = multiselect_filter("Filter by Acquisition Purpose", purposes)

client_types = sorted(df['client_type'].unique())
selected_client_types = multiselect_filter("Filter by Client Type", client_types)

# Applying Filters
filtered_df = df[
    (df['country'].isin(selected_countries)) &
    (df['region'].isin(selected_regions)) &
    (df['acquisition_purpose'].isin(selected_purposes)) &
    (df['client_type'].isin(selected_client_types))
]

st.markdown(f"**Showing data for {len(filtered_df):,} sold properties.**")

if len(filtered_df) == 0:
    st.warning("No data found for the selected filters. Please adjust your criteria.")
    st.stop()

# --- 3. DASHBOARD MODULES ---
col1, col2 = st.columns(2)

# Module 1: Buyer Segmentation Overview
with col1:
    st.subheader("Buyer Segmentation Overview")
    segment_counts = filtered_df['buyers_type'].value_counts().reset_index()
    segment_counts.columns = ['Buyer Type', 'Count']
    
    fig_pie = px.pie(
        segment_counts, 
        values='Count', 
        names='Buyer Type',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

# Module 2: Investor Behavior Dashboard
with col2:
    st.subheader("Investor Behavior Dashboard")
    # We will show the investment pattern (Area vs Price) per cluster
    fig_scatter = px.scatter(
        filtered_df,
        x='floor_area_sqft',
        y='sale_price',
        color='buyers_type',
        title='Investment Patterns: Area vs. Sale Price',
        labels={'floor_area_sqft': 'Floor Area (sqft)', 'sale_price': 'Sale Price ($)', 'buyers_type': 'Buyer Segment'},
        opacity=0.6,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_scatter, use_container_width=True)


st.divider()

col3, col4 = st.columns([1.5, 1])

# Module 3: Geographic Buyer Analysis
with col3:
    st.subheader("Geographic Buyer Analysis")
    
    # Applying Group by region and buyer type
    geo_data = filtered_df.groupby(['region', 'buyers_type']).size().reset_index(name='Count')
    
    # To keep the chart readable, taking only the Top 15 Regions by volume if there are too many
    top_regions = filtered_df['region'].value_counts().head(15).index
    geo_data_top = geo_data[geo_data['region'].isin(top_regions)]
    
    fig_bar = px.bar(
        geo_data_top,
        x='Count',
        y='region',
        color='buyers_type',
        orientation='h',
        title='Buyer Segments across Top 15 Regions',
        labels={'region': 'Region', 'Count': 'Number of Properties', 'buyers_type': 'Buyer Segment'},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)

# Module 4: Segment Insights Panel
with col4:
    st.subheader("Segment Insights Panel")
    st.markdown("Descriptive Statistics (Averages) per Cluster:")
    
    # Calculating statistics
    insights = filtered_df.groupby('buyers_type')[['age', 'sale_price', 'floor_area_sqft', 'satisfaction_score']].mean().round(2)
    
    # Renaming columns for presentation
    insights.columns = ['Avg Age', 'Avg Price ($)', 'Avg Area (sqft)', 'Avg Satisfaction (1-5)']
    insights.index.name = 'Buyer Segment'
    
    # Displaying as a beautiful dataframe
    st.dataframe(insights, use_container_width=True)
