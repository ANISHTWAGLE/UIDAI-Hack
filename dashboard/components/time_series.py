"""
Time-Series Stress Evolution Component
Visualizes stress trends using aggregated data.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def create_window_class_summary(df):
    """Create summary chart by window class (short/mid/long term)."""
    if 'window_class' not in df.columns:
        return None
    
    # Aggregate by window class
    summary = df.groupby('window_class').agg({
        'eur_mean': 'mean',
        'eur_std': 'mean',
        'stress_percentile': 'mean',
        'operators_needed': 'sum',
        'district': 'count'
    }).reset_index()
    summary = summary.rename(columns={'district': 'district_count'})
    
    # Order window classes
    order = ['short_term', 'mid_term', 'long_term']
    summary['window_class'] = pd.Categorical(summary['window_class'], categories=order, ordered=True)
    summary = summary.sort_values('window_class')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=summary['window_class'],
        y=summary['eur_mean'],
        name='Avg EUR Mean',
        marker_color='#DC2626'
    ))
    
    fig.update_layout(
        title="Average Stress by Time Window",
        xaxis_title="Window Class",
        yaxis_title="Average EUR Mean",
        height=350,
        template="plotly_white"
    )
    
    return fig


def create_enrolment_update_comparison(df):
    """Create comparison chart of enrolments vs updates by state."""
    if 'avg_daily_enrolments' not in df.columns or 'avg_daily_updates' not in df.columns:
        return None
    
    # Aggregate by state
    state_summary = df.groupby('state').agg({
        'avg_daily_enrolments': 'sum',
        'avg_daily_updates': 'sum'
    }).reset_index()
    
    # Sort by total activity
    state_summary['total'] = state_summary['avg_daily_enrolments'] + state_summary['avg_daily_updates']
    state_summary = state_summary.nlargest(15, 'total')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=state_summary['state'],
        y=state_summary['avg_daily_enrolments'],
        name='Avg Daily Enrolments',
        marker_color='#3B82F6'
    ))
    
    fig.add_trace(go.Bar(
        x=state_summary['state'],
        y=state_summary['avg_daily_updates'],
        name='Avg Daily Updates',
        marker_color='#10B981'
    ))
    
    fig.update_layout(
        title="Top 15 States: Enrolments vs Updates",
        xaxis_title="State",
        yaxis_title="Average Daily Count",
        barmode='group',
        height=400,
        template="plotly_white",
        xaxis_tickangle=45
    )
    
    return fig


def create_stress_distribution(df):
    """Create histogram of stress percentile distribution."""
    if 'stress_percentile' not in df.columns:
        return None
    
    fig = px.histogram(
        df,
        x='stress_percentile',
        nbins=20,
        color_discrete_sequence=['#6366F1'],
        title="Distribution of Stress Percentile Across Districts"
    )
    
    # Add threshold lines
    fig.add_vline(x=85, line_dash="dash", line_color="#DC2626", 
                  annotation_text="Critical (85%)")
    fig.add_vline(x=50, line_dash="dash", line_color="#F59E0B",
                  annotation_text="Warning (50%)")
    
    fig.update_layout(
        xaxis_title="Stress Percentile",
        yaxis_title="Number of Districts",
        height=350,
        template="plotly_white"
    )
    
    return fig


def render_time_series(df):
    """Render the time-series analysis component."""
    st.subheader("📈 Stress Evolution Analysis")
    
    st.markdown("""
    **Purpose:** Understand stress patterns across different time windows and regions.
    - **Short-term** (< 30 days): Recent volatility
    - **Mid-term** (30-90 days): Sustained patterns
    - **Long-term** (> 90 days): Structural issues
    """)
    
    # Window class summary
    st.markdown("### ⏱️ Stress by Time Window")
    fig_window = create_window_class_summary(df)
    if fig_window:
        st.plotly_chart(fig_window, use_container_width=True)
    
    # Window class breakdown
    if 'window_class' in df.columns:
        col1, col2, col3 = st.columns(3)
        with col1:
            short = len(df[df['window_class'] == 'short_term'])
            st.metric("Short-term", f"{short} districts")
        with col2:
            mid = len(df[df['window_class'] == 'mid_term'])
            st.metric("Mid-term", f"{mid} districts")
        with col3:
            long = len(df[df['window_class'] == 'long_term'])
            st.metric("Long-term", f"{long} districts")
    
    st.markdown("---")
    
    # Enrolments vs Updates
    st.markdown("### 📊 Enrolments vs Updates by State")
    fig_compare = create_enrolment_update_comparison(df)
    if fig_compare:
        st.plotly_chart(fig_compare, use_container_width=True)
    
    st.markdown("---")
    
    # Stress distribution
    st.markdown("### 📉 Stress Percentile Distribution")
    fig_dist = create_stress_distribution(df)
    if fig_dist:
        st.plotly_chart(fig_dist, use_container_width=True)
    
    # Key observations
    if 'stress_percentile' in df.columns:
        st.markdown("### 🔍 Key Observations")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            critical_pct = (df['stress_percentile'] > 85).mean() * 100
            st.metric("Critical Districts", f"{critical_pct:.1f}%", 
                     help="Districts with stress > 85th percentile")
        
        with col2:
            avg_stress = df['stress_percentile'].mean()
            st.metric("Average Stress", f"{avg_stress:.1f}%")
        
        with col3:
            max_stress_district = df.loc[df['stress_percentile'].idxmax()]
            st.metric("Highest Stress", 
                     f"{max_stress_district['district'][:20]}...",
                     f"{max_stress_district['stress_percentile']:.1f}%")
