"""
Infrastructure Stress Heatmap Component
Folium-based map with OpenStreetMap tiles showing district-level stress.
"""
import pandas as pd
import folium
from folium.plugins import HeatMap
import streamlit as st
from streamlit_folium import st_folium


# Color mappings based on stress category
CATEGORY_COLORS = {
    'Critical': '#DC2626',    # Red
    'Warning': '#F59E0B',     # Yellow/Amber
    'Normal': '#10B981'       # Green
}

# Color mappings based on recommendation
RECOMMENDATION_COLORS = {
    'Mobile Aadhaar Van': '#DC2626',      # Red - highest stress
    'Permanent Centre': '#991B1B',         # Dark red
    'Extra Counters': '#F59E0B',           # Amber
    'Semi-Permanent Support': '#FBBF24',   # Light amber
    'Temporary Mobile Camp': '#EF4444',    # Light red
    'Monitor Closely': '#84CC16',          # Light green
    'Monitor / No Action': '#10B981'       # Green
}


def create_base_map():
    """Create base OpenStreetMap centered on India."""
    m = folium.Map(
        location=[22.5, 82.5],
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    return m


def add_heatmap_layer(m, df):
    """Add heatmap layer based on EUR mean values."""
    valid_df = df[df['lat'].notna() & df['lon'].notna()].copy()
    
    if len(valid_df) == 0:
        return m
    
    # Normalize EUR mean for heat intensity
    max_eur = valid_df['eur_mean'].max()
    if max_eur > 0:
        valid_df['heat_weight'] = valid_df['eur_mean'] / max_eur
    else:
        valid_df['heat_weight'] = 0.5
    
    heat_data = valid_df[['lat', 'lon', 'heat_weight']].values.tolist()
    
    HeatMap(
        heat_data,
        radius=20,
        blur=15,
        max_zoom=10,
        gradient={
            0.0: '#10B981',   # Green
            0.4: '#FBBF24',   # Yellow
            0.7: '#F59E0B',   # Amber
            1.0: '#DC2626'    # Red
        }
    ).add_to(m)
    
    return m


def add_stress_markers(m, df, show_details=True):
    """Add circle markers for each district colored by recommendation."""
    valid_df = df[df['lat'].notna() & df['lon'].notna()].copy()
    
    for _, row in valid_df.iterrows():
        # Get color based on recommendation
        rec = row.get('recommendation', 'Monitor / No Action')
        color = RECOMMENDATION_COLORS.get(rec, '#10B981')
        
        # Get stress percentile for radius
        stress_pct = row.get('stress_percentile', 50)
        radius = max(5, min(15, stress_pct / 10))
        
        # Build popup content
        popup_html = f"""
        <div style="font-family: Arial; min-width: 200px;">
            <h4 style="margin: 0; color: #1E3A5F;">{row['district']}</h4>
            <p style="margin: 2px 0; color: #6B7280;">{row['state']}</p>
            <hr style="margin: 5px 0;">
            <table style="width: 100%; font-size: 12px;">
                <tr><td><b>EUR Mean:</b></td><td>{row.get('eur_mean', 0):.1f}</td></tr>
                <tr><td><b>Stress %:</b></td><td>{stress_pct:.1f}%</td></tr>
                <tr><td><b>Operators Needed:</b></td><td>{row.get('operators_needed', 0)}</td></tr>
                <tr><td><b>Recommendation:</b></td><td style="color: {color}; font-weight: bold;">{rec}</td></tr>
            </table>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=radius,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(m)
    
    return m


def add_legend(m):
    """Add a legend to the map."""
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000;
                background-color: white; padding: 10px; border-radius: 5px;
                border: 2px solid #ccc; font-family: Arial;">
        <h4 style="margin: 0 0 8px 0; color: #1E3A5F;">Stress Level</h4>
        <p style="margin: 4px 0;"><span style="background: #DC2626; width: 15px; height: 15px; 
           display: inline-block; border-radius: 50%; margin-right: 5px;"></span>Critical (Van/Centre)</p>
        <p style="margin: 4px 0;"><span style="background: #F59E0B; width: 15px; height: 15px; 
           display: inline-block; border-radius: 50%; margin-right: 5px;"></span>Warning (Extra Counters)</p>
        <p style="margin: 4px 0;"><span style="background: #10B981; width: 15px; height: 15px; 
           display: inline-block; border-radius: 50%; margin-right: 5px;"></span>Normal (Monitor)</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    return m


def render_heatmap(df):
    """Main function to render the heatmap component."""
    st.subheader("🗺️ Infrastructure Stress Heatmap")
    
    st.markdown("""
    **Interpretation Guide:**
    - 🔴 **Red clusters** → Structural failure - need permanent intervention
    - 🟡 **Yellow/Orange** → Rising stress - temporary measures needed
    - 🟢 **Green** → Adequate coverage - monitoring only
    """)
    
    # Map options
    col1, col2 = st.columns(2)
    with col1:
        show_heatmap = st.checkbox("Show Heat Layer", value=True)
    with col2:
        show_markers = st.checkbox("Show District Markers", value=True)
    
    # Create map
    m = create_base_map()
    
    valid_df = df[df['lat'].notna() & df['lon'].notna()].copy()
    
    if len(valid_df) == 0:
        st.warning("No geocoded locations available for mapping.")
        return
    
    if show_heatmap:
        m = add_heatmap_layer(m, valid_df)
    
    if show_markers:
        m = add_stress_markers(m, valid_df)
    
    m = add_legend(m)
    
    # Render map
    st_folium(m, width=None, height=500, returned_objects=[])
    
    # Summary statistics
    st.markdown("---")
    st.markdown("### 📊 Coverage Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = len(df)
        st.metric("Total Districts", total)
    
    with col2:
        critical_count = len(df[df['eur_category'] == 'Critical'])
        st.metric("🔴 Critical", critical_count)
    
    with col3:
        warning_count = len(df[df['eur_category'] == 'Warning'])
        st.metric("🟡 Warning", warning_count)
    
    with col4:
        normal_count = len(df[df['eur_category'] == 'Normal'])
        st.metric("🟢 Normal", normal_count)
    
    # Top stressed districts table
    if st.checkbox("Show Top 10 Stressed Districts", value=False):
        top_stressed = df.nlargest(10, 'stress_percentile')[
            ['state', 'district', 'eur_mean', 'stress_percentile', 'recommendation', 'operators_needed']
        ].reset_index(drop=True)
        top_stressed.index = top_stressed.index + 1
        st.dataframe(top_stressed, use_container_width=True)
