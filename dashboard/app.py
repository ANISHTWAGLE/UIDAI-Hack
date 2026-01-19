"""
Aadhaar Infrastructure Decision Dashboard
=========================================
A decision-driven government dashboard for infrastructure analysis.
Uses OpenStreetMap via Folium - no proprietary APIs.

Run with: streamlit run dashboard/app.py
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dashboard.data_loader import (
    load_intervention_data, 
    get_filtered_data,
    get_state_list,
    get_district_list,
    get_category_list,
    get_window_class_list
)
from dashboard.components.heatmap import render_heatmap
from dashboard.components.time_series import render_time_series
from dashboard.components.scatter import render_scatter
from dashboard.components.recommendation_engine import render_recommendation_engine
from dashboard.components.action_table import render_action_table
from dashboard.components.rankings import render_rankings
from dashboard.components.capacity_gap import render_capacity_gap


# Page configuration
st.set_page_config(
    page_title="Aadhaar Infrastructure Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Government-appropriate styling */
    .main {
        background-color: #F9FAFB;
    }
    
    /* Header styling */
    .dashboard-header {
        background: linear-gradient(135deg, #1E3A5F 0%, #2D5A87 100%);
        padding: 1.5rem 2rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        color: white;
    }
    
    .dashboard-header h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    .dashboard-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1rem;
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #E5E7EB;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Critical color */
    .critical { color: #DC2626; }
    .warning { color: #F59E0B; }
    .normal { color: #10B981; }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1E3A5F;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: white;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 4px;
        padding: 10px 20px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def main():
    # Header
    st.markdown("""
    <div class="dashboard-header">
        <h1>🏛️ Aadhaar Infrastructure Decision Dashboard</h1>
        <p>Governance Decision Engine | Powered by OpenStreetMap</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_intervention_data()
    
    # Sidebar filters
    with st.sidebar:
        st.markdown("## 🔍 Filters")
        
        # State filter
        selected_state = st.selectbox(
            "State",
            options=get_state_list(df),
            index=0
        )
        
        # District filter (dependent on state)
        selected_district = st.selectbox(
            "District",
            options=get_district_list(df, selected_state),
            index=0
        )
        
        # Category filter
        selected_category = st.selectbox(
            "Stress Category",
            options=get_category_list(),
            index=0
        )
        
        st.markdown("---")
        
        # Summary stats
        st.markdown("## 📊 Quick Stats")
        
        filtered_df = get_filtered_data(df, selected_state, selected_district, selected_category)
        
        total = len(filtered_df)
        critical = len(filtered_df[filtered_df['eur_category'] == 'Critical'])
        warning = len(filtered_df[filtered_df['eur_category'] == 'Warning'])
        normal = len(filtered_df[filtered_df['eur_category'] == 'Normal'])
        
        st.metric("Total Locations", total)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🔴 Critical", critical)
            st.metric("🟢 Normal", normal)
        with col2:
            st.metric("🟡 Warning", warning)
        
        st.markdown("---")
        st.markdown("### 📖 Color Guide")
        st.markdown("""
        🔴 **Critical** — Permanent intervention  
        🟡 **Warning** — Temporary measures  
        🟢 **Normal** — Stable operations
        """)
    
    # Apply filters
    filtered_df = get_filtered_data(df, selected_state, selected_district, selected_category)
    
    if filtered_df.empty:
        st.warning("No data matches the selected filters. Please adjust your selection.")
        return
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🗺️ Stress Map",
        "📈 Trends",
        "🎯 Decisions",
        "🧠 Engine",
        "📋 Actions",
        "🏆 Rankings",
        "🧮 Capacity"
    ])
    
    with tab1:
        render_heatmap(filtered_df)
    
    with tab2:
        render_time_series(filtered_df)
    
    with tab3:
        render_scatter(filtered_df)
    
    with tab4:
        render_recommendation_engine(filtered_df)
    
    with tab5:
        render_action_table(filtered_df)
    
    with tab6:
        render_rankings(filtered_df)
    
    with tab7:
        render_capacity_gap(filtered_df)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.85rem;">
        <p>Decision-Driven Government Dashboard | No Proprietary APIs | OpenStreetMap</p>
        <p>Built for government deployment with minimal external dependencies</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
