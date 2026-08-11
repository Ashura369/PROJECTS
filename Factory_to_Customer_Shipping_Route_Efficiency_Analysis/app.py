import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Set Streamlit page configuration
st.set_page_config(
    page_title="Nassau Candy Industries - Shipping Route Efficiency Analysis",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling with clean tabs and no blue box background
st.markdown("""
<style>
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 16px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-size: 1.75rem !important;
        font-weight: 700 !important;
    }
    
    /* Header Container */
    .main-header {
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
        padding: 24px;
        border-radius: 12px;
        border-left: 6px solid #0284c7;
        margin-bottom: 24px;
    }
    .main-header h1 {
        color: #f8fafc;
        font-size: 1.9rem;
        font-weight: 800;
        margin: 0;
        padding: 0;
    }
    .main-header p {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 6px;
        margin-bottom: 0;
    }
    
    /* Section Headings */
    .section-title {
        color: #e2e8f0;
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 18px;
        margin-bottom: 12px;
        border-bottom: 2px solid #334155;
        padding-bottom: 6px;
    }
    
    /* Tab Styling: Clean transparent tabs with subtle indicator, NO blue block */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
        background-color: transparent !important;
        border-bottom: 1px solid #334155;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        padding: 8px 12px;
        color: #94a3b8 !important;
        font-weight: 600;
        font-size: 0.95rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #38bdf8 !important;
        border-bottom: 2px solid #38bdf8 !important;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #1e293b !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        color: #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

# State coordinates mapping for maps
STATE_COORDS = {
    # US States
    'Alabama': (32.806671, -86.791130, 'AL', 'United States'),
    'Alaska': (61.370716, -152.404419, 'AK', 'United States'),
    'Arizona': (33.729759, -111.431221, 'AZ', 'United States'),
    'Arkansas': (34.969704, -92.373123, 'AR', 'United States'),
    'California': (36.116203, -119.681564, 'CA', 'United States'),
    'Colorado': (39.059811, -105.311104, 'CO', 'United States'),
    'Connecticut': (41.597782, -72.755371, 'CT', 'United States'),
    'Delaware': (39.318523, -75.507141, 'DE', 'United States'),
    'District Of Columbia': (38.897438, -77.026817, 'DC', 'United States'),
    'District of Columbia': (38.897438, -77.026817, 'DC', 'United States'),
    'Florida': (27.766279, -81.686783, 'FL', 'United States'),
    'Georgia': (33.040619, -83.643074, 'GA', 'United States'),
    'Hawaii': (21.094318, -157.498337, 'HI', 'United States'),
    'Idaho': (44.240459, -114.478828, 'ID', 'United States'),
    'Illinois': (40.349457, -88.986137, 'IL', 'United States'),
    'Indiana': (39.849426, -86.258278, 'IN', 'United States'),
    'Iowa': (42.011539, -93.210526, 'IA', 'United States'),
    'Kansas': (38.526600, -96.726486, 'KS', 'United States'),
    'Kentucky': (37.668140, -84.670067, 'KY', 'United States'),
    'Louisiana': (31.169546, -91.867805, 'LA', 'United States'),
    'Maine': (44.693947, -69.381927, 'ME', 'United States'),
    'Maryland': (39.063946, -76.802101, 'MD', 'United States'),
    'Massachusetts': (42.230171, -71.530106, 'MA', 'United States'),
    'Michigan': (43.326618, -84.536095, 'MI', 'United States'),
    'Minnesota': (45.694454, -93.900192, 'MN', 'United States'),
    'Mississippi': (32.741646, -89.678696, 'MS', 'United States'),
    'Missouri': (38.456085, -92.288368, 'MO', 'United States'),
    'Montana': (46.921925, -110.454353, 'MT', 'United States'),
    'Nebraska': (41.125370, -98.268082, 'NE', 'United States'),
    'Nevada': (38.313515, -117.055374, 'NV', 'United States'),
    'New Hampshire': (43.452492, -71.563896, 'NH', 'United States'),
    'New Jersey': (40.298904, -74.521011, 'NJ', 'United States'),
    'New Mexico': (34.840515, -106.248482, 'NM', 'United States'),
    'New York': (42.165726, -74.948051, 'NY', 'United States'),
    'North Carolina': (35.630066, -79.806419, 'NC', 'United States'),
    'North Dakota': (47.528912, -99.784012, 'ND', 'United States'),
    'Ohio': (40.388783, -82.764915, 'OH', 'United States'),
    'Oklahoma': (35.565342, -96.928917, 'OK', 'United States'),
    'Oregon': (44.572021, -122.070938, 'OR', 'United States'),
    'Pennsylvania': (40.590752, -77.209755, 'PA', 'United States'),
    'Rhode Island': (41.680893, -71.511780, 'RI', 'United States'),
    'South Carolina': (33.856892, -80.945007, 'SC', 'United States'),
    'South Dakota': (44.299782, -99.438828, 'SD', 'United States'),
    'Tennessee': (35.747845, -86.692345, 'TN', 'United States'),
    'Texas': (31.054487, -97.563461, 'TX', 'United States'),
    'Utah': (40.150032, -111.862434, 'UT', 'United States'),
    'Vermont': (44.045876, -72.710686, 'VT', 'United States'),
    'Virginia': (37.769337, -78.169968, 'VA', 'United States'),
    'Washington': (47.400902, -121.490494, 'WA', 'United States'),
    'West Virginia': (38.491226, -80.954453, 'WV', 'United States'),
    'Wisconsin': (44.268543, -89.616508, 'WI', 'United States'),
    'Wyoming': (42.755966, -107.302490, 'WY', 'United States'),
    # Canadian Provinces
    'Alberta': (53.933271, -116.576504, 'AB', 'Canada'),
    'British Columbia': (53.726668, -127.647621, 'BC', 'Canada'),
    'Manitoba': (53.760861, -98.813876, 'MB', 'Canada'),
    'New Brunswick': (46.565316, -66.461916, 'NB', 'Canada'),
    'Newfoundland and Labrador': (53.135509, -57.660436, 'NL', 'Canada'),
    'Newfoundland And Labrador': (53.135509, -57.660436, 'NL', 'Canada'),
    'Nova Scotia': (44.681987, -63.744311, 'NS', 'Canada'),
    'Ontario': (51.253775, -85.323214, 'ON', 'Canada'),
    'Prince Edward Island': (46.510712, -63.416814, 'PE', 'Canada'),
    'Quebec': (52.939916, -73.549136, 'QC', 'Canada'),
    'Saskatchewan': (52.939916, -106.450868, 'SK', 'Canada')
}

@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, 'Dataset', 'Nassau Candy Distributor Visualisation.csv'),
        os.path.join(base_dir, 'Nassau Candy Distributor Visualisation.csv'),
        os.path.join(base_dir, 'Dataset', 'Nassau Candy Distributor.csv'),
        os.path.join('Dataset', 'Nassau Candy Distributor Visualisation.csv'),
        'Nassau Candy Distributor Visualisation.csv'
    ]
    csv_path = None
    for cand in candidates:
        if os.path.exists(cand):
            csv_path = cand
            break
            
    if csv_path is None:
        raise FileNotFoundError(f"Could not find Nassau Candy Distributor Visualisation.csv. Looked in: {candidates}")
        
    df = pd.read_csv(csv_path)
    
    # Parse dates safely (removing timezone if present)
    df['Order Date'] = pd.to_datetime(df['Order Date']).dt.tz_localize(None)
    df['Shipping Date'] = pd.to_datetime(df['Shipping Date'], format='%d-%m-%Y')
    
    # Calculate Lead Time / Delay metrics
    df['Delay in Days'] = (df['Shipping Date'] - df['Order Date']).dt.days
    
    # Calculate Total Months Delay
    total_months = (df['Shipping Date'].dt.year - df['Order Date'].dt.year) * 12 + (df['Shipping Date'].dt.month - df['Order Date'].dt.month)
    df['Delay Months'] = total_months
    df['Delay in Years'] = (total_months / 12.0).round(1)
    df['Delay in Years Int'] = total_months // 12
    df['Delay in Month Remainder'] = total_months % 12
    
    # Standard vs Expedited Group
    expedited_modes = ['First Class', 'Second Class', 'Same Day']
    df['Shipping Mode (group)'] = df['Shipping Mode'].apply(lambda x: 'Expedited Group' if x in expedited_modes else 'Standard Shipping')
    
    return df

df_raw = load_data()

# ==============================================================================
# SIDEBAR: DEVELOPER CREDITS & FILTERS
# ==============================================================================
with st.sidebar:
    # Developer Credits Section at top of sidebar
    st.markdown("""
        <div style='display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 20px;'>
            <b style='margin-bottom: 10px; font-size: 15px; font-weight: 900;'>Developer Credits:</b>
            <div style='display: flex; gap: 10px; flex-wrap: wrap;'>
                <a href='https://github.com/pradhans369' target='_blank'>
                    <img src='https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white' style='border-radius: 4px;'>
                </a>
                <a href='https://www.linkedin.com/in/pradhans369/' target='_blank'>
                    <img src='https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white' style='border-radius: 4px;'>
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    st.title("Control Panel & Filters")
    st.markdown("Filter analytics by timeline, geography, shipping method, and delay threshold.")

    # 1. Date Range Filter
    min_date = df_raw['Order Date'].min().date()
    max_date = df_raw['Order Date'].max().date()
    selected_dates = st.date_input(
        "Order Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # 2. Country Filter
    all_countries = sorted(df_raw['Country'].dropna().unique().tolist())
    selected_countries = st.multiselect("Country", options=all_countries, default=all_countries)

    # 3. Region Filter
    available_regions = sorted(df_raw[df_raw['Country'].isin(selected_countries)]['Region'].dropna().unique().tolist())
    selected_regions = st.multiselect("Region", options=available_regions, default=available_regions)

    # 4. State / Province Selector
    available_states = sorted(df_raw[
        (df_raw['Country'].isin(selected_countries)) &
        (df_raw['Region'].isin(selected_regions))
    ]['State'].dropna().unique().tolist())
    selected_states = st.multiselect("State / Province", options=available_states, default=available_states)

    # 5. Shipping Mode Filter
    all_ship_modes = sorted(df_raw['Shipping Mode'].dropna().unique().tolist())
    selected_ship_modes = st.multiselect("Shipping Mode", options=all_ship_modes, default=all_ship_modes)

    # 6. Lead-Time Threshold Slider
    min_delay = int(df_raw['Delay in Days'].min())
    max_delay = int(df_raw['Delay in Days'].max())
    selected_lead_threshold = st.slider(
        "Lead-Time Delay Filter (Max Days)",
        min_value=min_delay,
        max_value=max_delay,
        value=max_delay,
        step=10,
        help="Filter out orders exceeding a specific lead-time threshold (in days)."
    )

    # Reset Filters Button
    if st.button("Reset All Filters", use_container_width=True):
        st.rerun()

    st.markdown("---")
    st.caption(f"Showing {len(df_raw):,} total available orders.")

# Apply Filters
if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    start_dt, end_dt = selected_dates
    date_mask = (df_raw['Order Date'].dt.date >= start_dt) & (df_raw['Order Date'].dt.date <= end_dt)
else:
    date_mask = True

df = df_raw[
    date_mask &
    (df_raw['Country'].isin(selected_countries)) &
    (df_raw['Region'].isin(selected_regions)) &
    (df_raw['State'].isin(selected_states)) &
    (df_raw['Shipping Mode'].isin(selected_ship_modes)) &
    (df_raw['Delay in Days'] <= selected_lead_threshold)
]

# ==============================================================================
# MAIN PAGE HEADER & KPI CARDS (All Numbers in Clean Integers)
# ==============================================================================
st.markdown("""
<div class="main-header">
    <h1>Nassau Candy Industries - Factory to Customer Shipping Route Efficiency Analysis</h1>
    <p>Operational logistics intelligence, route benchmarking, transit bottlenecks, and cost-efficiency trade-offs.</p>
</div>
""", unsafe_allow_html=True)

if len(df) == 0:
    st.warning("No data matches the selected filter criteria. Please adjust your sidebar filters.")
    st.stop()

# Top KPI Metric Cards (Formatted as Integers with No Floating Decimals)
col1, col2, col3, col4, col5 = st.columns(5)
total_sales = int(round(df['Sales Per Order'].sum()))
total_profit = int(round(df['Gross Profit Per Order'].sum()))
total_cost = int(round(df['Total Cost Per Order'].sum()))
total_shipments = len(df)
avg_delay_days = int(round(df['Delay in Days'].mean()))
avg_delay_years = round(avg_delay_days / 365.25, 1)

with col1:
    st.metric("Total Sales", f"${total_sales:,}")
with col2:
    st.metric("Total Profits", f"${total_profit:,}")
with col3:
    st.metric("Total Costs", f"${total_cost:,}")
with col4:
    st.metric("Total Shipments", f"{total_shipments:,}")
with col5:
    st.metric("Avg. Shipping Delay", f"{avg_delay_days:,} Days", f"{avg_delay_years:.1f} Years")

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# TAB NAVIGATION FOR DASHBOARD MODULES
# ==============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Route Efficiency & Speed Ranking",
    "Geographic Sales & Congestion Maps",
    "Regional & Shipping Mode Performance",
    "Bottleneck & Cost Trade-Off Analysis",
    "Data Explorer"
])

# ------------------------------------------------------------------------------
# TAB 1: Route Efficiency & Speed Ranking (Pages 2 & 3)
# ------------------------------------------------------------------------------
with tab1:
    st.markdown('<div class="section-title">Route Efficiency and Speed Benchmarking</div>', unsafe_allow_html=True)
    
    # 1. Ranking Top 20 Routes Fastest to Slowest (Page 2)
    state_delay = df.groupby('State')['Delay in Days'].mean().reset_index()
    top20_fastest = state_delay.sort_values(by='Delay in Days', ascending=True).head(20)
    
    fig_page2 = px.bar(
        top20_fastest,
        x='Delay in Days',
        y='State',
        orientation='h',
        title='Ranking Top 20 Routes Fastest to Slowest (Average Lead Time in Days)',
        labels={'Delay in Days': 'Avg. Delay in Days', 'State': 'Destination State'},
        text='Delay in Days',
        color='Delay in Days',
        color_continuous_scale=['#0ea5e9', '#38bdf8', '#f43f5e']
    )
    fig_page2.update_traces(
        texttemplate='%{text:.0f} days',
        textposition='outside',
        marker_line_color='#ffffff',
        marker_line_width=1
    )
    fig_page2.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis=dict(range=[0, max(top20_fastest['Delay in Days'].max() * 1.15, 1700)]),
        height=650,
        coloraxis_showscale=False,
        template='plotly_dark',
        margin=dict(l=40, r=40, t=60, b=40)
    )
    st.plotly_chart(fig_page2, use_container_width=True)
    
    with st.expander("Analytical Observations: Route Speed Ranking"):
        st.markdown("""
        - **Systemic Multi-Year Delay**: Even the top-performing states (such as New Jersey at ~1,338 days and Georgia at ~1,339 days) exhibit average transit durations exceeding 3.6 years. This confirms that delays are company-wide rather than confined to isolated remote routes.
        - **Fastest States**: New Jersey, Georgia, Missouri, Idaho, and Wisconsin lead in relative delivery performance.
        - **Severely Congested Endpoints**: North Dakota and West Virginia exhibit the longest transit times (~1,638 days, or 4.5 years), representing critical bottlenecks in destination fulfillment.
        """)

    st.markdown("---")
    
    # 2. Top 10 States Giving Most Profits at Different Shipping Modes (Page 3)
    st.markdown('<div class="section-title">State Profitability by Shipping Mode</div>', unsafe_allow_html=True)
    
    mode_state_profit = df.groupby(['Shipping Mode', 'State'])['Gross Profit Per Order'].mean().reset_index()
    mode_state_profit['Rank'] = mode_state_profit.groupby('Shipping Mode')['Gross Profit Per Order'].rank(ascending=False, method='first')
    top10_per_mode = mode_state_profit[mode_state_profit['Rank'] <= 10].sort_values(by=['Shipping Mode', 'Gross Profit Per Order'], ascending=[True, True])
    
    fig_page3 = px.bar(
        top10_per_mode,
        x='Gross Profit Per Order',
        y='State',
        color='Shipping Mode',
        facet_col='Shipping Mode',
        facet_col_wrap=2,
        title='Top 10 States Giving Most Profits at Different Shipping Modes',
        labels={'Gross Profit Per Order': 'Avg. Gross Profit Per Order ($)', 'State': 'State'},
        text='Gross Profit Per Order',
        color_discrete_map={
            'Standard Class': '#0ea5e9',
            'Second Class': '#10b981',
            'First Class': '#f43f5e',
            'Same Day': '#f59e0b'
        }
    )
    fig_page3.update_traces(
        texttemplate='$%{text:.2f}',
        textposition='outside',
        marker_line_color='#ffffff',
        marker_line_width=0.8
    )
    fig_page3.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig_page3.update_layout(
        height=800,
        template='plotly_dark',
        margin=dict(l=40, r=40, t=80, b=40),
        showlegend=True
    )
    st.plotly_chart(fig_page3, use_container_width=True)
    
    with st.expander("Analytical Observations: Profitability Across Shipping Modes"):
        st.markdown("""
        - **Premium Modes Margin**: First Class and Same Day shipments generate higher average profit per order in key states such as Maryland ($11.20) and Missouri ($11.03).
        - **Standard Class Consistency**: Standard Class demonstrates stable profit margins ($8.00 - $10.50) across the highest order volumes.
        - **Cross-Subsidization Opportunity**: High-margin states can be prioritized for carrier contract renegotiations and direct line-haul logistics.
        """)

# ------------------------------------------------------------------------------
# TAB 2: Geographic Sales & Congestion Maps (Pages 4 & 5)
# ------------------------------------------------------------------------------
with tab2:
    st.markdown('<div class="section-title">Geographic Sales & Congestion Mapping</div>', unsafe_allow_html=True)
    
    col_map1, col_map2 = st.columns(2)
    
    # State-level aggregation for mapping
    state_map_df = df.groupby(['Country', 'State']).agg({
        'Sales Per Order': 'sum',
        'Gross Profit Per Order': 'sum',
        'Delay in Days': 'mean',
        'Customer ID': 'count'
    }).reset_index().rename(columns={'Customer ID': 'Shipments'})
    
    # Attach coordinates and codes
    state_map_df['Lat'] = state_map_df['State'].apply(lambda s: STATE_COORDS.get(s, (None, None, None, None))[0])
    state_map_df['Lon'] = state_map_df['State'].apply(lambda s: STATE_COORDS.get(s, (None, None, None, None))[1])
    state_map_df['Code'] = state_map_df['State'].apply(lambda s: STATE_COORDS.get(s, (None, None, None, None))[2])
    
    state_map_df = state_map_df.dropna(subset=['Lat', 'Lon'])
    
    with col_map1:
        # 3. Total Sales from Each State of USA and Canada (Page 4)
        fig_page4 = px.scatter_geo(
            state_map_df,
            lat='Lat',
            lon='Lon',
            color='Country',
            size='Sales Per Order',
            hover_name='State',
            hover_data={
                'Lat': False,
                'Lon': False,
                'Country': True,
                'Sales Per Order': ':.2f',
                'Shipments': True
            },
            text='Code',
            title='Total Sales from Each State of USA and Canada',
            color_discrete_map={
                'United States': '#0284c7',
                'Canada': '#f97316'
            },
            size_max=36
        )
        fig_page4.update_geos(
            scope='north america',
            showcountries=True,
            showsubunits=True,
            subunitcolor="#475569",
            countrycolor="#64748b",
            bgcolor='#0f172a',
            showland=True,
            landcolor='#1e293b'
        )
        fig_page4.update_layout(
            template='plotly_dark',
            height=580,
            margin=dict(l=0, r=0, t=50, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_page4, use_container_width=True)
        
    with col_map2:
        # 4. Geographic Congestion Hotspots: Average Delivery Delays (Page 5)
        fig_page5 = px.scatter_geo(
            state_map_df,
            lat='Lat',
            lon='Lon',
            color='Delay in Days',
            size='Shipments',
            hover_name='State',
            hover_data={
                'Lat': False,
                'Lon': False,
                'Country': True,
                'Delay in Days': ':.0f',
                'Shipments': True
            },
            text='Code',
            title='Geographic Congestion Hotspots: Average Delivery Delays',
            color_continuous_scale=['#0284c7', '#38bdf8', '#fca5a5', '#f43f5e', '#881337'],
            range_color=[1137, 1638],
            size_max=36
        )
        fig_page5.update_geos(
            scope='north america',
            showcountries=True,
            showsubunits=True,
            subunitcolor="#475569",
            countrycolor="#64748b",
            bgcolor='#0f172a',
            showland=True,
            landcolor='#1e293b'
        )
        fig_page5.update_layout(
            template='plotly_dark',
            height=580,
            margin=dict(l=0, r=0, t=50, b=0),
            coloraxis_colorbar=dict(title="Avg. Delay (Days)")
        )
        st.plotly_chart(fig_page5, use_container_width=True)
        
    with st.expander("Analytical Observations: Geographic Sales Distribution and Congestion Hotspots"):
        st.markdown("""
        - **Market Disparity**: The United States accounts for the vast majority of overall sales volume (over 97%), led by California ($27,917.40), New York ($15,541.03), and Texas ($13,416.09). Canadian expansion provinces account for the remaining volume, led by Ontario ($814.57) and Alberta ($530.32).
        - **Northern Congestion Corridor**: A distinct, continuous geographical corridor of elevated delivery delay is visible extending from Iowa and North Dakota up through Saskatchewan and Manitoba (shaded in red/dark rose).
        - **Metro Bottleneck in District of Columbia**: The District of Columbia exhibits severe localized transit delay despite high shipping density, indicating urban distribution hub congestion.
        """)

# ------------------------------------------------------------------------------
# TAB 3: Regional & Shipping Mode Performance (Pages 6 & 7)
# ------------------------------------------------------------------------------
with tab3:
    st.markdown('<div class="section-title">Regional Performance and Shipping Mode Comparison</div>', unsafe_allow_html=True)
    
    col_p6_1, col_p6_2, col_p6_3 = st.columns([1.2, 1, 1])
    
    with col_p6_1:
        st.markdown("##### City Delivery Delays in Months and Years")
        city_delays = df.groupby(['Country', 'City']).agg({
            'Delay Months': 'mean',
            'Delay in Years': 'mean',
            'Customer ID': 'count'
        }).reset_index().rename(columns={
            'Delay Months': 'Avg. Delay Months',
            'Delay in Years': 'Avg. Delay in Years',
            'Customer ID': 'Shipments'
        })
        city_delays['Avg. Delay Months'] = city_delays['Avg. Delay Months'].round(0).astype(int)
        city_delays['Avg. Delay in Years'] = city_delays['Avg. Delay in Years'].round(1)
        
        st.dataframe(
            city_delays.sort_values(by='Avg. Delay Months', ascending=False),
            height=420,
            use_container_width=True,
            hide_index=True
        )
        
    with col_p6_2:
        st.markdown("##### Regions with High Avg. Delay in Days")
        region_delays = df.groupby('Region')['Delay in Days'].mean().reset_index().sort_values(by='Delay in Days', ascending=False)
        fig_p6b = px.bar(
            region_delays,
            x='Region',
            y='Delay in Days',
            color='Region',
            text='Delay in Days',
            color_discrete_sequence=['#6366f1', '#3b82f6', '#0ea5e9', '#06b6d4']
        )
        fig_p6b.update_traces(
            texttemplate='%{text:.0f}',
            textposition='outside',
            marker_line_color='#ffffff',
            marker_line_width=1
        )
        fig_p6b.update_layout(
            yaxis=dict(range=[0, 1600]),
            template='plotly_dark',
            height=420,
            showlegend=False,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_p6b, use_container_width=True)
        
    with col_p6_3:
        st.markdown("##### Expedited vs. Standard Shipping")
        group_delays = df.groupby('Shipping Mode (group)')['Delay in Days'].mean().reset_index()
        fig_p6c = px.bar(
            group_delays,
            x='Shipping Mode (group)',
            y='Delay in Days',
            color='Shipping Mode (group)',
            text='Delay in Days',
            color_discrete_map={
                'Expedited Group': '#0284c7',
                'Standard Shipping': '#0284c7'
            }
        )
        fig_p6c.update_traces(
            texttemplate='%{text:.0f}',
            textposition='outside',
            marker_line_color='#ffffff',
            marker_line_width=1
        )
        fig_p6c.update_layout(
            yaxis=dict(range=[0, 1600]),
            template='plotly_dark',
            height=420,
            showlegend=False,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_p6c, use_container_width=True)
        
    st.markdown("---")
    
    # 7. Comparing Performance Across Different Shipping Modes Based on Profits (Page 7)
    st.markdown('<div class="section-title">Shipping Mode Profit Share by Country</div>', unsafe_allow_html=True)
    
    col_pie1, col_pie2 = st.columns(2)
    
    mode_profit_country = df.groupby(['Country', 'Shipping Mode'])['Gross Profit Per Order'].sum().reset_index()
    
    with col_pie1:
        df_pie_ca = mode_profit_country[mode_profit_country['Country'] == 'Canada']
        if len(df_pie_ca) > 0:
            fig_pie_ca = px.pie(
                df_pie_ca,
                names='Shipping Mode',
                values='Gross Profit Per Order',
                title='Canada - Profit Share by Shipping Mode',
                color='Shipping Mode',
                color_discrete_map={
                    'Standard Class': '#f59e0b',
                    'Second Class': '#ef4444',
                    'First Class': '#1d4ed8',
                    'Same Day': '#60a5fa'
                },
                hole=0.3
            )
            fig_pie_ca.update_traces(
                textposition='inside',
                textinfo='percent+label',
                marker=dict(line=dict(color='#ffffff', width=1.5))
            )
            fig_pie_ca.update_layout(
                template='plotly_dark',
                height=450,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pie_ca, use_container_width=True)
        else:
            st.info("No Canadian data available for current filter selection.")
            
    with col_pie2:
        df_pie_us = mode_profit_country[mode_profit_country['Country'] == 'United States']
        if len(df_pie_us) > 0:
            fig_pie_us = px.pie(
                df_pie_us,
                names='Shipping Mode',
                values='Gross Profit Per Order',
                title='United States - Profit Share by Shipping Mode',
                color='Shipping Mode',
                color_discrete_map={
                    'Standard Class': '#f59e0b',
                    'Second Class': '#ef4444',
                    'First Class': '#1d4ed8',
                    'Same Day': '#60a5fa'
                },
                hole=0.3
            )
            fig_pie_us.update_traces(
                textposition='inside',
                textinfo='percent+label',
                marker=dict(line=dict(color='#ffffff', width=1.5))
            )
            fig_pie_us.update_layout(
                template='plotly_dark',
                height=450,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pie_us, use_container_width=True)
        else:
            st.info("No US data available for current filter selection.")
            
    with st.expander("Analytical Observations: Shipping Mode Performance & Profit Breakdown"):
        st.markdown("""
        - **The Expedited Shipping Paradox**: Expedited shipments (Same Day, First Class, Second Class) average **1,374 days**, while Standard Shipping averages **1,361 days**. Customers paying for expedited delivery experience no tangible lead-time advantage.
        - **Regional Uniformity**: Transit times across the Interior (1,376 days), Pacific (1,366 days), Gulf (1,365 days), and Atlantic (1,357 days) regions differ by less than 1.5%, indicating a centralized manufacturing/dispatch backlog rather than regional transit friction.
        - **Profit Generation Share**: Standard Class dominates overall profit contribution (76.7% in Canada, 59.6% in the US), followed by Second Class (16.6% in Canada, 19.5% in the US).
        """)

# ------------------------------------------------------------------------------
# TAB 4: Bottleneck & Cost Trade-Off Analysis (Pages 8 & 9)
# ------------------------------------------------------------------------------
with tab4:
    st.markdown('<div class="section-title">Bottleneck Detection & Cost-Delay Trade-off</div>', unsafe_allow_html=True)
    
    col_bt1, col_bt2 = st.columns(2)
    
    state_quad = df.groupby(['Country', 'State', 'Region']).agg({
        'Delay in Days': 'mean',
        'Customer ID': 'count',
        'Total Cost Per Order': 'mean',
        'Sales Per Order': 'sum'
    }).reset_index().rename(columns={'Customer ID': 'Shipment Volume'})
    
    with col_bt1:
        # 8. Geographic Bottleneck Analysis: Volume vs. Shipping Delay (Page 8)
        fig_page8 = px.scatter(
            state_quad,
            x='Delay in Days',
            y='Shipment Volume',
            color='Region',
            hover_name='State',
            hover_data={
                'Country': True,
                'Delay in Days': ':.0f',
                'Shipment Volume': True,
                'Total Cost Per Order': ':.2f'
            },
            title='Geographic Bottleneck Analysis: Volume vs. Shipping Delay',
            labels={
                'Delay in Days': 'Avg. Delay in Days',
                'Shipment Volume': 'Count of Shipments (Orders)'
            },
            color_discrete_map={
                'Atlantic': '#f97316',
                'Gulf': '#10b981',
                'Interior': '#0284c7',
                'Pacific': '#ef4444'
            }
        )
        
        # Quadrant reference lines
        fig_page8.add_vline(x=1380, line_dash="solid", line_color="#94a3b8", line_width=1.5, annotation_text="Threshold (1,380 Days)", annotation_position="top right")
        fig_page8.add_hline(y=200, line_dash="solid", line_color="#94a3b8", line_width=1.5, annotation_text="Threshold (200 Orders)", annotation_position="bottom right")
        
        fig_page8.update_traces(marker=dict(size=10, line=dict(width=1, color='#ffffff')))
        fig_page8.update_layout(
            template='plotly_dark',
            height=580,
            xaxis=dict(range=[0, 1750]),
            yaxis=dict(range=[-50, max(state_quad['Shipment Volume'].max() * 1.1, 2100)]),
            margin=dict(l=40, r=40, t=60, b=40)
        )
        st.plotly_chart(fig_page8, use_container_width=True)
        
    with col_bt2:
        # 9. Cost vs. Delay Trade-off Analysis (Page 9)
        fig_page9 = px.scatter(
            state_quad,
            x='Delay in Days',
            y='Total Cost Per Order',
            color='State',
            facet_col='Country',
            hover_name='State',
            hover_data={
                'Delay in Days': ':.0f',
                'Total Cost Per Order': ':.2f',
                'Shipment Volume': True
            },
            title='Avg. Delay in Days vs. Avg. Total Cost Per Order by Country',
            labels={
                'Delay in Days': 'Avg. Delay in Days',
                'Total Cost Per Order': 'Avg. Total Cost Per Order ($)'
            }
        )
        fig_page9.update_traces(marker=dict(size=10, line=dict(width=1, color='#ffffff')))
        fig_page9.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig_page9.update_layout(
            template='plotly_dark',
            height=580,
            xaxis=dict(range=[0, 1750]),
            yaxis=dict(range=[0, 9]),
            showlegend=False,
            margin=dict(l=40, r=40, t=60, b=40)
        )
        st.plotly_chart(fig_page9, use_container_width=True)
        
    with st.expander("Analytical Observations: Bottleneck Matrix & Cost-Delay Dynamics"):
        st.markdown("""
        - **Critical Bottleneck Quadrant (Top-Right)**: States located in the upper-right quadrant (exceeding 200 orders and 1,380 days of delay) represent high-volume routes with unacceptable transit lag. These routes should receive primary investment in dedicated warehouse staging.
        - **High-Volume Drivers**: California (over 2,000 orders) and New York (over 1,000 orders) dominate total order frequency while experiencing severe average delays (~1,300 - 1,350 days).
        - **Cost-Delay Trade-off**: Manufacturing cost per order ranges between $3.50 and $8.00 and exhibits no inverse correlation with delivery speed, confirming that higher-cost products do not receive expedited logistics prioritization.
        """)

# ------------------------------------------------------------------------------
# TAB 5: Data Explorer
# ------------------------------------------------------------------------------
with tab5:
    st.markdown('<div class="section-title">Raw Data Explorer & Export</div>', unsafe_allow_html=True)
    st.markdown(f"Viewing active subset of **{len(df):,}** order records.")
    
    st.dataframe(df, use_container_width=True, height=500)
    
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Dataset as CSV",
        data=csv_data,
        file_name="Nassau_Candy_Filtered_Shipping_Analysis.csv",
        mime="text/csv",
        use_container_width=True
    )
