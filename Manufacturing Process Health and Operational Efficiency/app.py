import streamlit as st
import sys
from streamlit.web.cli import main
from streamlit.web import cli as stcli
import streamlit.components.v1 as components

# -------------------------------------------------------------------
st.set_page_config(
    page_title="ThalesEnterprises",
    layout="wide"
)
# -------------------------------------------------------------------

st.title("Thales Enterprises | Factory Health and Operations")

# -------------------------------------------------------------------

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

# -------------------------------------------------------------------

# Making the segment for Main Presentation

@st.dialog("Tableau Dashboard", width="large")
def full_screen(embed):
    components.html(embed, height=1000, scrolling=True)

left, center, right = st.columns([1,17,1])

embed_main_dashboard = st.secrets["main_dashboard"]

with center:
    col1, col2 = st.columns([2,5])

    with col1:
        st.subheader("Plant Stability & Quality Control Overview")
        st.write("This macro-level intercative dashboard provides a of bird-eye view of all the plots with a comprehensive assessment of overall plant stability, equipment risk exposure, and operational readiness.")
        st.write("""
        * **Total No. of Machines With Maintenance Status (Donut Chart):** Breaks down the fleet into distinct maintenance risk categories—highlighting Critical Risk, Healthy, and Monitor proportions to guide immediate technician dispatch.
        * **Total No. of Machines With Efficiency Status (Donut Chart):** Visualizes the distribution of assets across High, Medium, and Low efficiency tiers to measure plant-wide operational output.
        * **Total No. of Machines With Operation Mode (Donut Chart):** Displays the active operational state of machinery (Active, Idle, Maintenance) to evaluate resource utilization.
        * **Average Production Speed with Efficiency Status (Line Graph):** Correlates production output speeds against efficiency tiers to prove how higher operating velocity scales with performance categorization.
        """)
    with col2:
        if st.button("Maximize", key='full_screen'):
            full_screen(embed_main_dashboard)
        components.html(embed_main_dashboard, height=750, scrolling=True)


# -------------------------------------------------------------------

# creating navigation tabs for dashboards

# making tabs section
type = [
    "Production Performance Diagnostics",
    "Efficiency Status and Cross Metrics Diagnostics",
    "Centralized Visualisation of Existing Problems"
]

selection = st.selectbox("Select Operational Report", options=type, index=None)

if selection == 'Production Performance Diagnostics':
    st.subheader("Production Performance Diagnostics with Quality & Error Analysis")
    st.write("This diagnostic panel correlates critical sensor behaviors against quality control metrics and production speed trends to isolate operational bottlenecks.")
    st.write("""
    * **Quality Control Defect Rate at Different Sensors (Scatter Matrix):** Plots defect percentages against Power Consumption, Temperature, and Vibration metrics, categorized by load states to identify environment-driven flaws.
    * **Production Speed Trends (Line Chart):** Tracks day-to-day fluctuations in manufacturing velocity to flag sudden performance drops.
    * **Units Produced Per Hour Across Different Machines (Bar Chart):** Compares output rates across individual machine IDs to find high performers versus underperforming assets.
    * **Identifying Quality Bottlenecks (Bar Charts):** Evaluates average production speeds and defect counts across efficiency classes to pinpoint structural limitations.
    * **Machines at Different Quality Control Defect Rate (Ranked Bar Chart):** Ranks individual machine IDs from lowest to highest defect frequency for targeted quality auditing.
    * **Comparing Different Sensor Stability Across Different Operation Modes (Matrix Grid):** Cross-analyzes Power Consumption, Temperature, and Vibration stability under Active, Idle, and Maintenance modes.
    """)

    left1, center1, right1 = st.columns([1,17,1])
    with center1:
        embed_1 = st.secrets["Production_Performance_Diagnostics_with_Quailty_and_Error_Analysis"]
        if st.button("Maximize", key='full_screen_1'):
            full_screen(embed_main_dashboard)
        components.html(embed_1, width=1200, height=1000, scrolling=True)

if selection == 'Efficiency Status and Cross Metrics Diagnostics':
    st.subheader("Efficiency Status and Cross-Metrics Diagnostics")
    st.write("This section cross-analyzes shift schedules and environmental parameters against plant efficiency statuses and error frequencies.")
    st.write("""
    * **Efficiency Across Operation Modes and Shifts (Grouped Bar Chart):** Evaluates average production speeds broken down granularly across Morning, Afternoon, Evening, and Night shifts alongside operational states.
    * **Checking How Often Machines Fall Into High, Medium, and Low (Monthly Donut Charts):** Tracks month-over-month shifts (January, February, March) in plant-wide efficiency proportions.
    * **Avg. Quality Control with Different Levels of Temperature (Bar Chart):** Measures how varying temperature thresholds (High, Normal, Warning) impact defect rates.
    * **Avg. Error Rate with Different Vibration levels (Bar Chart):** Quantifies error frequencies across Critical, Moderate, and Stable vibration spectrums.
    * **Avg. Power Consumption with Efficiency Status (Bar Chart):** Contrasts power draw against Low, Medium, and High efficiency tiers to monitor energy efficiency.
    """)

    left1, center1, right1 = st.columns([1,17,1])
    with center1:
        embed_1 = st.secrets["Efficiency_Status_and_Cross_Metrics_Diagnostics"]
        if st.button("Maximize", key='full_screen_2'):
            full_screen(embed_main_dashboard)
        components.html(embed_1, width=1200, height=1000, scrolling=True)

if selection == 'Centralized Visualisation of Existing Problems':
    st.subheader("Centralized Visualisation of Existing Problems")
    st.write("This centralized risk view highlights active plant anomalies by combining temporal defect tracking with multi-sensor performance clusters.")
    st.write("""
    * **Avg. Quality Control and Avg. Packet Loss at Different Days of the Month (Dual-Axis Line Chart):** Traces daily synchronized trends between product defect rates and network/sensor packet loss over a 31-day period.
    * **Scatter Plot with Avg. Production Efficiency with Multiple Sensors (Scatter Grid):** Maps production speeds against temperature, power consumption, and vibration metrics, filtering machines by risk and efficiency status.
    * **Total No. of Machines With Maintenance Status (Donut Chart):** Summarizes current critical risk versus healthy asset ratios to highlight immediate plant vulnerability.
    * **Total No. of Machines With Efficiency Status (Donut Chart):** Displays the macro ratio of high-performing vs low-performing machinery.
    * **Total No. of Machines With Operation Mode (Donut Chart):** Details active fleet utilization percentages.
    * **Average Production Speed with Efficiency Status (Line Chart):** Maps velocity changes against operational efficiency tiers.
    """)

    left1, center1, right1 = st.columns([1,17,1])
    with center1:
        embed_1 = st.secrets["Efficiency_Status_and_Cross_Metrics_Diagnostics"]
        if st.button("Maximize", key='full_screen_3'):
            full_screen(embed_main_dashboard)
        components.html(embed_1, width=1200, height=1000, scrolling=True)


# -------------------------------------------------------------------

if __name__ == '__main__':
    if st.runtime.exists():
        pass
    else:
        sys.argv = ['streamlit', 'run', sys.argv[0]]
        sys.exit(stcli.main())