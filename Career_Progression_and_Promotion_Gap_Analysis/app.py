import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ==============================================================================
# 1. PAGE CONFIGURATION & THEME STYLING
# ==============================================================================
st.set_page_config(
    page_title="Palo Alto Networks | Career & Retention Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Executive Dark Theme Styling
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    /* Ensure Sidebar is Open and Styled */
    [data-testid="stSidebar"] {
        background-color: #161B26;
        border-right: 1px solid #2E3440;
    }
    
    /* Header Container */
    .header-container {
        background: linear-gradient(135deg, #1E2640 0%, #0E1117 100%);
        padding: 24px;
        border-radius: 12px;
        border-left: 6px solid #FF4B4B;
        margin-bottom: 20px;
    }
    
    /* Metric Card Styling */
    .metric-card {
        background-color: #1E222D;
        border-radius: 10px;
        padding: 16px 20px;
        border: 1px solid #2E3440;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #FFFFFF;
        margin-top: 4px;
    }
    .metric-label {
        font-size: 13px;
        color: #A0AAB8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1E222D;
        border-radius: 6px;
        color: #A0AAB8;
        padding: 10px 20px;
        border: 1px solid #2E3440;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E222D !important;
        color: #FF4B4B !important;
        border-bottom: 3px solid #FF4B4B !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. DATA LOADING & PREPROCESSING
# ==============================================================================
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(base_dir, "Dataset", "Final Visualization Dataset.csv"),
        os.path.join(base_dir, "Final Visualization Dataset.csv"),
        os.path.join(base_dir, "Dataset", "Visualization Dataset.csv"),
        os.path.join(base_dir, "Visualization Dataset.csv"),
        "Dataset/Final Visualization Dataset.csv",
        "Final Visualization Dataset.csv",
        "../Dataset/Final Visualization Dataset.csv",
        "Dataset/Visualization Dataset.csv",
        "Visualization Dataset.csv"
    ]
    df = None
    for path in possible_paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                break
            except Exception:
                continue
            
    if df is None:
        st.error("Error: Dataset file 'Final Visualization Dataset.csv' not found!")
        st.stop()
        
    # Standardize Attrition column
    if 'Attrition' in df.columns:
        if df['Attrition'].dtype == object:
            attr_map = {'Yes': 1, 'No': 0, '1': 1, '0': 0, 'Left': 1, 'Retained': 0}
            df['Attrition'] = df['Attrition'].map(attr_map).fillna(0).astype(int)
        df['Attrition_Status'] = df['Attrition'].map({0: 'Retained', 1: 'Left'})
    else:
        df['Attrition'] = 0
        df['Attrition_Status'] = 'Retained'
    
    # Ensure calculated metrics exist
    if 'Promotion Gap Ratio' not in df.columns and 'Years At Company' in df.columns and 'Years Since Last Promotion' in df.columns:
        tenure = df['Years At Company'].replace(0, 0.5)
        df['Promotion Gap Ratio'] = (df['Years Since Last Promotion'] / tenure).round(2)
        
    if 'Role Stagnation Index' not in df.columns and 'Years At Company' in df.columns and 'Years In Current Role' in df.columns:
        tenure = df['Years At Company'].replace(0, 0.5)
        df['Role Stagnation Index'] = (df['Years In Current Role'] / tenure).round(2)
        
    if 'Training Intensity' not in df.columns and 'Years At Company' in df.columns and 'Training Times Last Year' in df.columns:
        tenure = df['Years At Company'].replace(0, 0.5)
        df['Training Intensity'] = (df['Training Times Last Year'] / tenure).round(2)

    # Ensure required label/cluster columns exist with fallback logic
    if 'Job Level Label' not in df.columns and 'Job Level' in df.columns:
        level_map = {1: 'Associate / Junior', 2: 'Mid-Level', 3: 'Senior', 4: 'Staff / Principal', 5: 'Director / VP'}
        df['Job Level Label'] = df['Job Level'].map(level_map).fillna('Mid-Level')

    if 'Manager Stability Indicator Labels' not in df.columns and 'Years With Curr Manager' in df.columns:
        def mgr_stability(yrs):
            if yrs < 1: return 'New Relationship'
            elif yrs <= 3: return 'Developing'
            elif yrs <= 6: return 'Stable'
            else: return 'Highly Stable'
        df['Manager Stability Indicator Labels'] = df['Years With Curr Manager'].apply(mgr_stability)

    if 'Promotion Risk Cluster' not in df.columns:
        def classify_cluster(row):
            if row.get('Years Since Last Promotion', 0) <= 1 and row.get('Performance Rating', 3) >= 3:
                return 'Fast-Track High Performers'
            elif row.get('Years In Current Role', 0) >= 4 and row.get('Job Level', 1) in [2, 3]:
                return 'Role-Stagnant Mid-Level'
            elif row.get('Years At Company', 0) >= 8 and row.get('Years Since Last Promotion', 0) >= 3:
                return 'Tenured & Stalled Seniors'
            else:
                return 'Early-Career Explorers'
        df['Promotion Risk Cluster'] = df.apply(classify_cluster, axis=1)

    return df

df_raw = load_data()


# ==============================================================================
# 3. SIDEBAR CONTROLS (USER CAPABILITIES) & CREDITS
# ==============================================================================
st.sidebar.title("Dashboard Controls")

st.sidebar.markdown("---")
st.sidebar.subheader("Organizational Filters")

# Department Filter
departments = ["All"] + sorted(df_raw['Department'].dropna().unique().tolist())
selected_dept = st.sidebar.selectbox("Department", departments)

# Job Role Filter
if selected_dept != "All":
    roles_available = sorted(df_raw[df_raw['Department'] == selected_dept]['Job Role'].dropna().unique().tolist())
else:
    roles_available = sorted(df_raw['Job Role'].dropna().unique().tolist())
selected_roles = st.sidebar.multiselect("Job Role(s)", roles_available, default=[])

# Seniority / Job Level Filter
job_levels = ["All"] + sorted(df_raw['Job Level Label'].dropna().unique().tolist())
selected_level = st.sidebar.selectbox("Career Stage / Job Level", job_levels)

# Cluster Explorer Filter
clusters = ["All"] + sorted(df_raw['Promotion Risk Cluster'].dropna().unique().tolist())
selected_cluster = st.sidebar.selectbox("Career Trajectory Cluster", clusters)

st.sidebar.markdown("---")
st.sidebar.subheader("Threshold Sliders")

promo_gap_threshold = st.sidebar.slider(
    "Promotion Gap Ratio Cutoff",
    min_value=0.0, max_value=1.0, value=0.30, step=0.05,
    help="Flags employees whose ratio of Years Since Promotion / Years At Company exceeds this value."
)

promo_years_threshold = st.sidebar.slider(
    "Years Without Promotion Cutoff",
    min_value=0, max_value=15, value=3, step=1,
    help="Flags employees waiting longer than these years for a promotion."
)

stagnation_threshold = st.sidebar.slider(
    "Role Stagnation Index Cutoff",
    min_value=0.0, max_value=1.0, value=0.50, step=0.05,
    help="Flags employees spending more than this fraction of company tenure in the same role."
)


# Filter Logic Application
df = df_raw.copy()

if selected_dept != "All":
    df = df[df['Department'] == selected_dept]
if selected_roles:
    df = df[df['Job Role'].isin(selected_roles)]
if selected_level != "All":
    df = df[df['Job Level Label'] == selected_level]
if selected_cluster != "All":
    df = df[df['Promotion Risk Cluster'] == selected_cluster]


# ==============================================================================
# 4. MAIN HEADER, CREDITS SECTION & SCORECARDS
# ==============================================================================
col_head1, col_head2 = st.columns([2, 1])

with col_head1:
    st.markdown("""
    <div class="header-container">
        <h1 style="margin:0; font-size:26px; font-weight:800; color:#FFFFFF;">
            Palo Alto Networks — Career Progression & Retention Intelligence
        </h1>
        <p style="margin:6px 0 0 0; color:#A0AAB8; font-size:14px;">
            Proactive workforce management platform analyzing career stagnation, promotion gap cliffs, and managerial continuity.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_head2:
    # Credits Section
    st.markdown("""
        <div style='display: flex; justify-content: flex-end; align-items: center; padding-top: 15px;'>
            <b style='margin-right: 15px; font-size: 16px;'>Credits : </b>
            <a href='https://github.com/pradhans369' target='_blank'>
                <img src='https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white' style='margin-right: 10px; border-radius: 8px;'>
            </a>
            <a href='https://www.linkedin.com/in/pradhans369/' target='_blank'>
                <img src='https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white' style='border-radius: 8px;'>
            </a>
        </div>
    """, unsafe_allow_html=True)

# Top KPI Summary Scorecards
total_headcount = len(df)
overall_attrition_count = df['Attrition'].sum() if 'Attrition' in df.columns else 0
overall_attrition_rate = (overall_attrition_count / total_headcount * 100) if total_headcount > 0 else 0
high_gap_count = len(df[df['Years Since Last Promotion'] >= promo_years_threshold])
high_risk_cluster_count = len(df[df['Promotion Risk Cluster'].isin(['Role-Stagnant Mid-Level', 'Tenured & Stalled Seniors'])])

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Employees Filtered</div>
        <div class="metric-value">{total_headcount:,}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Attrition Rate</div>
        <div class="metric-value" style="color: {'#FF4B4B' if overall_attrition_rate > 15 else '#00D26A'};">{overall_attrition_rate:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">High Promotion Gap ({promo_years_threshold}+ yrs)</div>
        <div class="metric-value" style="color: #FFA500;">{high_gap_count:,}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Stagnant Cluster Headcount</div>
        <div class="metric-value" style="color: #E74C3C;">{high_risk_cluster_count:,}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ==============================================================================
# 5. DASHBOARD MODULE TABS
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Career Path Clustering",
    "2. Promotion Gap Monitor",
    "3. Retention Opportunity Panel",
    "4. Managerial Insights"
])


# ------------------------------------------------------------------------------
# MODULE 1: CAREER PATH CLUSTERING DASHBOARD
# ------------------------------------------------------------------------------
with tab1:
    st.header("1. Career Path Clustering Dashboard (Unsupervised ML)")
    st.markdown("Identifies empirical career trajectory archetypes generated via K-Means clustering.")
    
    col_c1, col_c2 = st.columns([1, 1])
    
    with col_c1:
        st.subheader("Workforce Distribution Across Career Clusters")
        cluster_counts = df['Promotion Risk Cluster'].value_counts().reset_index()
        cluster_counts.columns = ['Promotion Risk Cluster', 'Count']
        
        fig_donut = px.pie(
            cluster_counts,
            names='Promotion Risk Cluster',
            values='Count',
            hole=0.45,
            color='Promotion Risk Cluster',
            color_discrete_map={
                'Fast-Track High Performers': '#00D26A',
                'Role-Stagnant Mid-Level': '#FFA500',
                'Tenured & Stalled Seniors': '#FF4B4B',
                'Early-Career Explorers': '#3498DB'
            }
        )
        fig_donut.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#0E1117', width=2)))
        fig_donut.update_layout(template="plotly_dark", height=400, showlegend=False)
        st.plotly_chart(fig_donut, width="stretch")

    with col_c2:
        st.subheader("Attrition Rate by Career Cluster")
        cluster_attr = df.groupby('Promotion Risk Cluster')['Attrition'].agg(['count', 'mean']).reset_index()
        cluster_attr['Attrition Rate %'] = (cluster_attr['mean'] * 100).round(1)
        
        fig_bar_attr = px.bar(
            cluster_attr,
            x='Promotion Risk Cluster',
            y='Attrition Rate %',
            color='Promotion Risk Cluster',
            text='Attrition Rate %',
            color_discrete_map={
                'Fast-Track High Performers': '#00D26A',
                'Role-Stagnant Mid-Level': '#FFA500',
                'Tenured & Stalled Seniors': '#FF4B4B',
                'Early-Career Explorers': '#3498DB'
            }
        )
        fig_bar_attr.update_traces(texttemplate='%{text}%', textposition='outside')
        fig_bar_attr.update_layout(template="plotly_dark", height=400, showlegend=False, yaxis_title="Attrition Rate (%)")
        st.plotly_chart(fig_bar_attr, width="stretch")

    st.markdown("---")
    st.subheader("Cluster Profile Summary: Career Trajectory Benchmarks")
    
    cluster_profiles = df.groupby('Promotion Risk Cluster').agg(
        Headcount=('Age', 'count'),
        Avg_Promotion_Gap_Ratio=('Promotion Gap Ratio', 'mean'),
        Avg_Role_Stagnation_Index=('Role Stagnation Index', 'mean'),
        Avg_Training_Intensity=('Training Intensity', 'mean'),
        Avg_Years_At_Company=('Years At Company', 'mean'),
        Attrition_Rate_Pct=('Attrition', lambda x: (x.mean() * 100).round(1))
    ).reset_index()
    
    # Format for display
    display_profiles = cluster_profiles.copy()
    display_profiles['Avg_Promotion_Gap_Ratio'] = display_profiles['Avg_Promotion_Gap_Ratio'].round(2)
    display_profiles['Avg_Role_Stagnation_Index'] = display_profiles['Avg_Role_Stagnation_Index'].round(2)
    display_profiles['Avg_Training_Intensity'] = display_profiles['Avg_Training_Intensity'].round(2)
    display_profiles['Avg_Years_At_Company'] = display_profiles['Avg_Years_At_Company'].round(1)
    
    st.dataframe(display_profiles, width="stretch")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Cluster Explorer: 2D Feature Space")
    fig_scatter = px.scatter(
        df,
        x='Role Stagnation Index',
        y='Promotion Gap Ratio',
        color='Promotion Risk Cluster',
        size='Years At Company',
        hover_data=['Job Role', 'Department', 'Years Since Last Promotion', 'Monthly Income'],
        color_discrete_map={
            'Fast-Track High Performers': '#00D26A',
            'Role-Stagnant Mid-Level': '#FFA500',
            'Tenured & Stalled Seniors': '#FF4B4B',
            'Early-Career Explorers': '#3498DB'
        }
    )
    fig_scatter.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig_scatter, width="stretch")


# ------------------------------------------------------------------------------
# MODULE 2: PROMOTION GAP MONITOR
# ------------------------------------------------------------------------------
with tab2:
    st.header("2. Promotion Gap Monitor")
    st.markdown("Monitors role-level stagnation and promotion gap cliffs pushing employees toward exit decisions.")
    
    col_p1, col_p2 = st.columns([1, 1])
    
    with col_p1:
        st.subheader("Average Promotion Gap Ratio by Job Role")
        role_gap = df.groupby('Job Role')['Promotion Gap Ratio'].mean().reset_index().sort_values('Promotion Gap Ratio', ascending=True)
        role_gap['Promotion Gap Ratio'] = role_gap['Promotion Gap Ratio'].round(2)
        
        fig_role_gap = px.bar(
            role_gap,
            x='Promotion Gap Ratio',
            y='Job Role',
            orientation='h',
            color='Promotion Gap Ratio',
            color_continuous_scale='Reds',
            text='Promotion Gap Ratio'
        )
        fig_role_gap.update_traces(textposition='outside')
        fig_role_gap.update_layout(template="plotly_dark", height=450, coloraxis_showscale=False)
        st.plotly_chart(fig_role_gap, width="stretch")

    with col_p2:
        st.subheader("The Promotion Freeze: Attrition Spike vs Years Without Promotion")
        promo_years_attr = df.groupby('Years Since Last Promotion')['Attrition'].agg(['count', 'mean']).reset_index()
        promo_years_attr['Attrition Rate %'] = (promo_years_attr['mean'] * 100).round(1)
        
        fig_freeze = px.line(
            promo_years_attr,
            x='Years Since Last Promotion',
            y='Attrition Rate %',
            markers=True,
            line_shape='spline',
            color_discrete_sequence=['#FF4B4B']
        )
        fig_freeze.add_vline(x=promo_years_threshold, line_dash="dash", line_color="yellow", annotation_text=f"{promo_years_threshold}+ Yrs Threshold")
        fig_freeze.update_layout(template="plotly_dark", height=450, yaxis_title="Attrition Rate (%)")
        st.plotly_chart(fig_freeze, width="stretch")

    st.markdown("---")
    st.subheader(f"High Promotion Gap Employee Identification (>= {promo_years_threshold} Years Without Promotion)")
    
    high_gap_df = df[
        (df['Years Since Last Promotion'] >= promo_years_threshold) |
        (df['Promotion Gap Ratio'] >= promo_gap_threshold)
    ][['Department', 'Job Role', 'Job Level Label', 'Years At Company', 'Years In Current Role', 'Years Since Last Promotion', 'Promotion Gap Ratio', 'Monthly Income', 'Attrition_Status']]
    
    st.markdown(f"Found **{len(high_gap_df):,}** employees matching high-gap criteria.")
    st.dataframe(high_gap_df, width="stretch")


# ------------------------------------------------------------------------------
# MODULE 3: RETENTION OPPORTUNITY PANEL
# ------------------------------------------------------------------------------
with tab3:
    st.header("3. Retention Opportunity Panel (Proactive Intervention)")
    st.markdown("Identifies **active employees (`Attrition == Retained`)** who are not yet disengaged, but exhibit career stagnation signals requiring immediate HR action.")
    
    # Active Employees Only
    active_df = df[df['Attrition'] == 0].copy()
    
    # Rule-Based Suggested Actions Engine
    def assign_action(row):
        if row['Years Since Last Promotion'] >= promo_years_threshold or row['Promotion Gap Ratio'] >= promo_gap_threshold:
            return "Immediate Promotion / Compensation Review"
        elif row['Role Stagnation Index'] >= stagnation_threshold:
            return "Lateral Role Rotation / New Project"
        elif row['Training Intensity'] < 0.25:
            return "Upskilling & Training Program"
        elif row['Manager Stability Indicator Labels'] == 'New Relationship':
            return "Manager Alignment & Mentorship"
        else:
            return "Regular Monitoring"

    active_df['Suggested Action'] = active_df.apply(assign_action, axis=1)
    
    col_r1, col_r2 = st.columns([1, 1])
    
    with col_r1:
        st.subheader("Retention Opportunity Matrix (Active Employees)")
        fig_matrix = px.scatter(
            active_df,
            x='Role Stagnation Index',
            y='Job Satisfaction',
            color='Suggested Action',
            size='Years Since Last Promotion',
            hover_data=['Job Role', 'Department', 'Years At Company', 'Monthly Income'],
            color_discrete_map={
                'Immediate Promotion / Compensation Review': '#FF4B4B',
                'Lateral Role Rotation / New Project': '#FFA500',
                'Upskilling & Training Program': '#3498DB',
                'Manager Alignment & Mentorship': '#9B59B6',
                'Regular Monitoring': '#2ECC71'
            }
        )
        fig_matrix.update_layout(template="plotly_dark", height=450)
        st.plotly_chart(fig_matrix, width="stretch")

    with col_r2:
        st.subheader("Intervention Summary: Suggested HR Actions")
        action_summary = active_df['Suggested Action'].value_counts().reset_index()
        action_summary.columns = ['Suggested Action', 'Count']
        
        fig_action_pie = px.pie(
            action_summary,
            names='Suggested Action',
            values='Count',
            color='Suggested Action',
            hole=0.4,
            color_discrete_map={
                'Immediate Promotion / Compensation Review': '#FF4B4B',
                'Lateral Role Rotation / New Project': '#FFA500',
                'Upskilling & Training Program': '#3498DB',
                'Manager Alignment & Mentorship': '#9B59B6',
                'Regular Monitoring': '#2ECC71'
            }
        )
        fig_action_pie.update_layout(template="plotly_dark", height=450, showlegend=True)
        st.plotly_chart(fig_action_pie, width="stretch")

    st.markdown("---")
    st.subheader("Actionable Employee Intervention Register")
    
    available_actions = list(active_df['Suggested Action'].unique())
    default_actions = [act for act in ["Immediate Promotion / Compensation Review", "Lateral Role Rotation / New Project"] if act in available_actions]

    action_filter = st.multiselect(
        "Filter by Recommended Action",
        options=available_actions,
        default=default_actions
    )
    
    filtered_action_df = active_df[active_df['Suggested Action'].isin(action_filter)][
        ['Department', 'Job Role', 'Job Level Label', 'Years At Company', 'Years In Current Role', 'Years Since Last Promotion', 'Job Satisfaction', 'Suggested Action']
    ]
    
    st.dataframe(filtered_action_df, width="stretch")
    
    # Download Button for HR Action Plan
    csv_data = filtered_action_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download HR Intervention Action Plan (CSV)",
        data=csv_data,
        file_name="HR_Retention_Action_Plan.csv",
        mime="text/csv"
    )


# ------------------------------------------------------------------------------
# MODULE 4: MANAGERIAL INSIGHT DASHBOARD
# ------------------------------------------------------------------------------
with tab4:
    st.header("4. Managerial & Leadership Insight Dashboard")
    st.markdown("Analyzes manager stability, leadership continuity, and team-level stagnation signals.")
    
    col_m1, col_m2 = st.columns([1, 1])
    
    with col_m1:
        st.subheader("Impact of Manager Relationship Stability on Attrition")
        mgr_attr = df.groupby('Manager Stability Indicator Labels')['Attrition'].agg(['count', 'mean']).reset_index()
        mgr_attr['Attrition Rate %'] = (mgr_attr['mean'] * 100).round(1)
        
        # Order categories
        order_map = {'New Relationship': 1, 'Developing': 2, 'Stable': 3, 'Highly Stable': 4}
        mgr_attr['Sort'] = mgr_attr['Manager Stability Indicator Labels'].map(order_map)
        mgr_attr = mgr_attr.sort_values('Sort')
        
        fig_mgr_bar = px.bar(
            mgr_attr,
            x='Manager Stability Indicator Labels',
            y='Attrition Rate %',
            color='Manager Stability Indicator Labels',
            text='Attrition Rate %',
            color_discrete_sequence=['#FF4B4B', '#FFA500', '#3498DB', '#00D26A']
        )
        fig_mgr_bar.update_traces(texttemplate='%{text}%', textposition='outside')
        fig_mgr_bar.update_layout(template="plotly_dark", height=450, showlegend=False, yaxis_title="Attrition Rate (%)")
        st.plotly_chart(fig_mgr_bar, width="stretch")

    with col_m2:
        st.subheader("Manager Tenure vs. Career Growth (Role Tenure)")
        fig_mgr_scatter = px.scatter(
            df,
            x='Years With Curr Manager',
            y='Years In Current Role',
            color='Promotion Risk Cluster',
            hover_data=['Job Role', 'Department', 'Years At Company'],
            color_discrete_map={
                'Fast-Track High Performers': '#00D26A',
                'Role-Stagnant Mid-Level': '#FFA500',
                'Tenured & Stalled Seniors': '#FF4B4B',
                'Early-Career Explorers': '#3498DB'
            }
        )
        fig_mgr_scatter.update_layout(template="plotly_dark", height=450)
        st.plotly_chart(fig_mgr_scatter, width="stretch")

    st.markdown("---")
    st.subheader("Departmental Leadership Continuity Summary")
    
    dept_mgr_summary = df.groupby('Department').agg(
        Total_Employees=('Age', 'count'),
        Avg_Years_With_Manager=('Years With Curr Manager', 'mean'),
        New_Manager_Relationship_Pct=('Manager Stability Indicator Labels', lambda x: ((x == 'New Relationship').mean() * 100).round(1)),
        Overall_Department_Attrition=('Attrition', lambda x: (x.mean() * 100).round(1))
    ).reset_index()
    
    dept_mgr_summary['Avg_Years_With_Manager'] = dept_mgr_summary['Avg_Years_With_Manager'].round(1)
    st.dataframe(dept_mgr_summary, width="stretch")
