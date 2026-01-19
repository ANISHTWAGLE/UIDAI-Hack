"""
Rule-Based Recommendation Engine
Displays pre-computed recommendations with auditable logic.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def render_recommendation_engine(df):
    """Render the recommendation engine component."""
    st.subheader("🧠 Infrastructure Recommendation Engine")
    
    st.markdown("""
    **Purpose:** Convert stress metrics into explicit administrative actions.
    
    This engine uses rule-based logic (no ML) for full auditability.
    All recommendations are pre-computed and stored in the dataset.
    """)
    
    # Decision logic reference
    with st.expander("📖 Decision Rules (Auditable Logic)", expanded=False):
        st.markdown("""
        | Condition | Recommendation | Rationale |
        |-----------|----------------|-----------|
        | High stress (>85%) + short-term | Mobile Aadhaar Van | Urgent temporary intervention |
        | High stress (>85%) + mid/long-term | Permanent Centre | Structural solution needed |
        | Medium stress (50-85%) + sustained | Extra Counters | Capacity augmentation |
        | Low stress (<50%) | Monitor / No Action | Within acceptable range |
        
        **Key Thresholds:**
        - **Stress Percentile >85%** → Critical intervention required
        - **Stress Percentile 50-85%** → Warning - temporary measures
        - **Stress Percentile <50%** → Normal operations
        """)
    
    st.markdown("---")
    
    # Recommendation distribution
    st.markdown("### 📊 Recommendation Distribution")
    
    if 'recommendation' in df.columns:
        rec_counts = df['recommendation'].value_counts()
        
        colors = {
            'Mobile Aadhaar Van': '#DC2626',
            'Permanent Centre': '#991B1B',
            'Extra Counters': '#F59E0B',
            'Semi-Permanent Support': '#FBBF24',
            'Temporary Mobile Camp': '#EF4444',
            'Monitor Closely': '#84CC16',
            'Monitor / No Action': '#10B981'
        }
        
        fig = px.pie(
            values=rec_counts.values,
            names=rec_counts.index,
            color=rec_counts.index,
            color_discrete_map=colors,
            title="Districts by Recommended Action"
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Recommendation metrics
    st.markdown("### 📈 Action Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        mobile_van = len(df[df['recommendation'] == 'Mobile Aadhaar Van'])
        st.metric("🚐 Mobile Vans Needed", mobile_van, 
                 help="Districts requiring mobile van deployment")
    
    with col2:
        permanent = len(df[df['recommendation'] == 'Permanent Centre'])
        st.metric("🏢 Permanent Centres", permanent,
                 help="Districts requiring new permanent centres")
    
    with col3:
        extra = len(df[df['recommendation'] == 'Extra Counters'])
        st.metric("🔧 Extra Counters", extra,
                 help="Districts requiring additional staff/counters")
    
    st.markdown("---")
    
    # Lookup tool
    st.markdown("### 🔍 District Lookup")
    
    lookup_district = st.selectbox(
        "Select a district to view its recommendation",
        options=["Select..."] + sorted(df['district'].unique().tolist())
    )
    
    if lookup_district != "Select...":
        district_row = df[df['district'] == lookup_district].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **District:** {district_row['district']}  
            **State:** {district_row['state']}  
            **Stress Percentile:** {district_row.get('stress_percentile', 0):.1f}%  
            **EUR Mean:** {district_row.get('eur_mean', 0):.2f}  
            """)
        
        with col2:
            rec = district_row.get('recommendation', 'Unknown')
            reason = district_row.get('reason', 'No reason provided')
            operators = district_row.get('operators_needed', 0)
            
            # Color based on recommendation
            if 'Van' in rec or 'Permanent' in rec:
                color = "#DC2626"
            elif 'Counter' in rec or 'Semi' in rec:
                color = "#F59E0B"
            else:
                color = "#10B981"
            
            st.markdown(f"""
            <div style="background: {color}20; padding: 15px; border-radius: 8px; border-left: 4px solid {color};">
                <h4 style="color: {color}; margin: 0;">📋 Recommendation: {rec}</h4>
                <p style="margin: 10px 0 0 0;"><b>Reason:</b> {reason}</p>
                <p style="margin: 5px 0 0 0;"><b>Operators Needed:</b> {operators}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Audit summary
    st.markdown("### 📋 Audit Summary")
    
    if 'recommendation' in df.columns:
        audit_df = df.groupby('recommendation').agg({
            'district': 'count',
            'operators_needed': 'sum',
            'stress_percentile': 'mean'
        }).reset_index()
        audit_df.columns = ['Recommendation', 'Districts', 'Total Operators', 'Avg Stress %']
        audit_df = audit_df.sort_values('Avg Stress %', ascending=False)
        
        st.dataframe(
            audit_df.style.format({
                'Avg Stress %': '{:.1f}%',
                'Total Operators': '{:.0f}'
            }),
            use_container_width=True,
            hide_index=True
        )
