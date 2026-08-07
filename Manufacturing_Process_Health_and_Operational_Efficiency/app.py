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
      
    st.subheader("Plant Stability & Quality Control Overview")
    st.write("This macro-level intercative dashboard provides a of bird-eye view of all the plots with a comprehensive assessment of overall plant stability, equipment risk exposure, and operational readiness.")

    if st.button("Maximize", key='full_screen'):
        full_screen(embed_main_dashboard)
    components.html(embed_main_dashboard, height=800, scrolling=True)

    # putting an expander
    with st.expander("Detailed Analysis"):
        st.write("""
        *   **Comparing Different Sensor Stability Across Different Operation Modes:** The average temperature, vibration, and power consumption remain relatively consistent across Active, Idle, and Maintenance modes, showing only very slight variations.
        *   **Production Speed Trends:** Production speed fluctuates significantly day-to-day over the 31-day period, bouncing erratically between a low of 271 and a high of 281 units per hour.
        *   **Scatter Plot with Avg. Production Efficiency with Multiple Sensors:** The data points are tightly grouped into three distinct vertical clusters (red, yellow, green) along the production speed axis, indicating that temperature, power consumption, and vibration readings are stratified based on specific speed brackets.
        *   **Identifying Quality Bottlenecks:** Counterintuitively, the average quality control defect rate is highest when the machine's efficiency status is "High," and lowest when the efficiency status is "Low."
        *   **Total No. of Machines With Maintenance Status:** Nearly half of the machines (49.83%) require monitoring, 29.99% are healthy, and 20.18% are classified as a critical risk.
        *   **Total No. of Machines With Efficiency Status:** The vast majority of machines (77.83%) operate at "Low" efficiency, with 19.19% at "Medium," and only a small fraction (2.99%) reaching "High" efficiency.
        *   **Total No. of Machines With Operation Mode:** Most machines (70.05%) are currently in "Active" mode, while 9.89% are in "Maintenance" and the remainder are "Idle."
        
        """)


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
    with st.expander("Detailed Analysis & Recommended Measures"):
        st.write("""
        * **Quality Control Defect Rate at Different Sensors (Scatter Matrix):** Plots defect percentages against Power Consumption, Temperature, and Vibration metrics, categorized by load states to identify environment-driven flaws.
            *   **Recommended Measure:** Implement a comprehensive sensor calibration audit across all load states to ensure environmental variables are accurately triggering preventive maintenance.
        * **Production Speed Trends (Line Chart):** Tracks day-to-day fluctuations in manufacturing velocity to flag sudden performance drops.
            *   **Recommended Measure:** Standardize shift changeovers and material feeding processes to stabilize the daily output rate and prevent mechanical stress caused by sudden speed changes.
        * **Units Produced Per Hour Across Different Machines (Bar Chart):** Compares output rates across individual machine IDs to find high performers versus underperforming assets.
            *   **Recommended Measure:** Replicate the exact settings of top-performing machines on underperforming machines to bridge the gap in production speeds.
        * **Identifying Quality Bottlenecks (Bar Charts):** Evaluates average production speeds and defect counts across efficiency classes to pinpoint structural limitations.
            *   **Recommended Measure:** Introduce a dynamic speed-capping protocol that automatically throttles machines down to "Medium" efficiency when real-time quality control sensors detect a rising defect rate.
        * **Machines at Different Quality Control Defect Rate (Ranked Bar Chart):** Ranks individual machine IDs from lowest to highest defect frequency for targeted quality auditing.
            *   **Recommended Measure:** Immediately schedule the machines with the highest defect rates for offline deep-cleaning, part replacement, and recalibration before they process any more raw materials.
        * **Comparing Different Sensor Stability Across Different Operation Modes (Matrix Grid):** Cross-analyzes Power Consumption, Temperature, and Vibration stability under Active, Idle, and Maintenance modes.
            *   **Recommended Measure:** Install secondary diagnostic sensors (such as acoustic monitors or high-speed visual inspection cameras) to catch errors that basic temperature/vibration sensors are missing.
        """)

    left1, center1, right1 = st.columns([1,17,1])
    with center1:
        embed_1 = st.secrets["Production_Performance_Diagnostics_with_Quailty_and_Error_Analysis"]
        if st.button("Maximize", key='full_screen_1'):
            full_screen(embed_1)
        components.html(embed_1, width=1200, height=1000, scrolling=True)

if selection == 'Efficiency Status and Cross Metrics Diagnostics':
    st.subheader("Efficiency Status and Cross-Metrics Diagnostics")
    st.write("This section cross-analyzes shift schedules and environmental parameters against plant efficiency statuses and error frequencies.")
    with st.expander("Detailed Analysis & Recommended Measures"):
        st.write("""
        *   **Efficiency Across Operation Modes and Shifts:** Average production speed is remarkably flat and consistent (hovering around 272–281 units/hr) regardless of the shift (Afternoon, Evening, Morning, Night) or the operation mode.
            *   **Recommended Measure:** Focus future optimization budgets on machine hardware upgrades and automation rather than staff training, as personnel are already performing consistently.
        *   **Checking How Often Machines Fall Into High, Medium, and Low:** The proportion of machines in Low, Medium, and High efficiency statuses remains almost completely static across January, February, and March (with Low efficiency dominating at ~78% each month).
            *   **Recommended Measure:** Initiate a capital expenditure review to replace aging baseline equipment or upgrade the central software governing machine operation limits.
        *   **Avg. Quality Control with Different Levels of Temperature:** The average quality control defect rate is identical (~5.00% to 5.01%) regardless of whether the machine's temperature state is High, Normal, or Warning.
            *   **Recommended Measure:** Redirect maintenance resources away from cooling systems and focus on other variables (like mechanical alignment or raw material quality) to solve the defect issue.
        *   **Avg. Error Rate with Different Vibration levels:** The average error rate is completely consistent (~7.50% to 7.52%) across Critical, Moderate, and Stable vibration levels.
            *   **Recommended Measure:** Re-evaluate and potentially loosen the vibration tolerance guidelines to ensure thresholds aren't overly sensitive and causing unnecessary machine shutdowns.
        *   **Avg. Power Consumption with Efficiency Status:** Average power consumption remains flat and unchanging (between 5.72 and 5.76 kW) across Low, Medium, and High efficiency statuses.
            *   **Recommended Measure:** Conduct an energy audit to identify parasitic power drains and optimize the idle/low-efficiency power states of the machines.
        """)

    left1, center1, right1 = st.columns([1,17,1])
    with center1:
        embed_2 = st.secrets["Efficiency_Status_and_Cross_Metrics_Diagnostics"]
        if st.button("Maximize", key='full_screen_2'):
            full_screen(embed_2)
        components.html(embed_2, width=1200, height=1000, scrolling=True)

if selection == 'Centralized Visualisation of Existing Problems':
    st.subheader("Centralized Visualisation of Existing Problems")
    st.write("This centralized risk view highlights active plant anomalies by combining temporal defect tracking with multi-sensor performance clusters.")
    with st.expander("Detailed Analysis & Recommended Measures"):
        st.write("""
        *   **Avg Quality Control and Avg Packet Loss at Different Days of the Month:** Both the quality control defect rate and packet loss experience highly erratic daily fluctuations over the 31-day period, suggesting instability over time, though their peaks and valleys do not perfectly mirror one another.
            *   **Recommended Measure:** Upgrade the factory's network hardware (routers/switches) or implement edge computing so machines rely less on constant cloud connectivity to maintain quality control.
        *   **Scatter Plot with Avg. Production Efficiency with Multiple Sensors:** Sensor metrics are again grouped into three tight, separated clusters, indicating distinct operational states based on production speed.
            *   **Recommended Measure:** Analyze the exact parameters of the optimal (highest speed/lowest defect) cluster. Program the factory's automated control systems to rigidly lock all machines into that specific temperature/power/vibration envelope.
        *   **Total No. of Machines With Maintenance Status:** 49.83% of machines are in the "Monitor" phase, 29.99% are "Healthy," and 20.18% pose a "Critical Risk."
            *   **Recommended Measure:** Shift from reactive to predictive maintenance using AI forecasting, and immediately prioritize servicing the 20.18% at critical risk to prevent catastrophic failures.
        *   **Total No. of Machines With Efficiency Status:** 77.83% of the machines are operating at "Low" efficiency, showing a widespread efficiency issue across the factory.
            *   **Recommended Measure:** Form a dedicated engineering task force to investigate this widespread baseline inefficiency. Conduct a pilot program on a small batch of machines to test new firmware.
        *   **Total No. of Machines With Operation Mode:** 70.05% of the machines are actively running, while a small portion (9.89%) is undergoing maintenance.
            *   **Recommended Measure:** Streamline the repair supply chain to ensure spare parts are always on-site, drastically reducing the time machines spend waiting in the maintenance queue.
        *   **Average Production Speed with Efficiency Status:** A line chart demonstrates a clear, linear relationship showing that as a machine's efficiency status improves from Low to Medium to High, its average production speed significantly increases.
            *   **Recommended Measure:** Incentivize floor managers based on overall machine efficiency ratings rather than pure output volume to encourage holistic machine care and maintenance.
        """)

    left1, center1, right1 = st.columns([1,17,1])
    with center1:
        embed_3 = st.secrets["Efficiency_Status_and_Cross_Metrics_Diagnostics"]
        if st.button("Maximize", key='full_screen_3'):
            full_screen(embed_3)
        components.html(embed_3, width=1200, height=1000, scrolling=True)


# -------------------------------------------------------------------

if __name__ == '__main__':
    if st.runtime.exists():
        pass
    else:
        sys.argv = ['streamlit', 'run', sys.argv[0]]
        sys.exit(stcli.main())