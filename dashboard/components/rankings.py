"""
Priority Rankings Component
Top stressed and best-served districts for budget allocation.
"""
import streamlit as st
import plotly.express as px
import pandas as pd


def create_top_stressed_chart(df, n=10):
    """Create horizontal bar chart for top stressed districts."""
    top_df = df.nlargest(n, 'stress_percentile')[['state', 'district', 'stress_percentile', 'eur_mean']]
    top_df['label'] = top_df['district'] + ' (' + top_df['state'].str[:3] + ')'
    
    fig = px.bar(
        top_df,
        y='label',
        x='stress_percentile',
        orientation='h',
        color='stress_percentile',
        color_continuous_scale=['#FBBF24', '#F59E0B', '#DC2626'],
        title=f"Top {n} Most Stressed Districts"
    )
    
    fig.update_layout(
        yaxis_title="",
        xaxis_title="Stress Percentile",
        height=400,
        template="plotly_white",
        coloraxis_showscale=False
    )
    
    return fig


def create_best_served_chart(df, n=10):
    """Create horizontal bar chart for best-served districts."""
    # Filter out very new districts (less data) and get lowest stress
    valid_df = df[df['stress_percentile'] > 0].copy()
    bottom_df = valid_df.nsmallest(n, 'stress_percentile')[['state', 'district', 'stress_percentile', 'eur_mean']]
    bottom_df['label'] = bottom_df['district'] + ' (' + bottom_df['state'].str[:3] + ')'
    
    fig = px.bar(
        bottom_df,
        y='label',
        x='stress_percentile',
        orientation='h',
        color='stress_percentile',
        color_continuous_scale=['#10B981', '#34D399', '#6EE7B7'],
        title=f"Top {n} Best-Served Districts (Lowest Stress)"
    )
    
    fig.update_layout(
        yaxis_title="",
        xaxis_title="Stress Percentile",
        height=400,
        template="plotly_white",
        coloraxis_showscale=False
    )
    
    return fig


def render_rankings(df):
    """Render the priority rankings component."""
    st.subheader("🏆 Priority Rankings")
    
    st.markdown("""
    **Purpose:** Support budget allocation, parliamentary answers, and public reporting.
    - **Most Stressed Districts** → Priority for intervention
    - **Best-Served Districts** → Potential for resource reallocation
    """)
    
    # Top charts side by side
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔴 Top 10 Most Stressed")
        fig_top = create_top_stressed_chart(df)
        st.plotly_chart(fig_top, use_container_width=True)
    
    with col2:
        st.markdown("### 🟢 Top 10 Best-Served")
        fig_best = create_best_served_chart(df)
        st.plotly_chart(fig_best, use_container_width=True)
    
    st.markdown("---")
    
    # Detailed tables
    st.markdown("### Most Stressed Districts (Details)")
    
    top_stressed = df.nlargest(10, 'stress_percentile')[
        ['state', 'district', 'eur_mean', 'stress_percentile', 
         'operators_needed', 'recommendation', 'reason']
    ].reset_index(drop=True)
    top_stressed.index = top_stressed.index + 1
    
    st.dataframe(
        top_stressed.style.format({
            'eur_mean': '{:.2f}',
            'stress_percentile': '{:.1f}%'
        }),
        use_container_width=True
    )
    
    st.markdown("---")
    
    st.markdown("### Best Served Districts (Details)")
    
    valid_df = df[df['stress_percentile'] > 0].copy()
    best_served = valid_df.nsmallest(10, 'stress_percentile')[
        ['state', 'district', 'eur_mean', 'stress_percentile', 
         'operators_needed', 'recommendation']
    ].reset_index(drop=True)
    best_served.index = best_served.index + 1
    
    st.dataframe(
        best_served.style.format({
            'eur_mean': '{:.2f}',
            'stress_percentile': '{:.1f}%'
        }),
        use_container_width=True
    )
    
    st.markdown("---")
    
    # State-level overview
    st.markdown("### 🗺️ State-Level Overview")
    
    state_summary = df.groupby('state').agg({
        'district': 'count',
        'stress_percentile': 'mean',
        'operators_needed': 'sum',
        'eur_mean': 'mean'
    }).reset_index()
    state_summary.columns = ['State', 'Districts', 'Avg Stress %', 'Total Operators', 'Avg EUR']
    
    # Sort by average stress
    state_summary = state_summary.sort_values('Avg Stress %', ascending=False)
    
    # Create bar chart
    fig = px.bar(
        state_summary.head(15),
        x='State',
        y='Avg Stress %',
        color='Avg Stress %',
        color_continuous_scale=['#10B981', '#F59E0B', '#DC2626'],
        title="Top 15 States by Average Stress Percentile"
    )
    
    fig.update_layout(
        xaxis_tickangle=45,
        height=400,
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Full state table
    if st.checkbox("Show All States", value=False):
        st.dataframe(
            state_summary.style.format({
                'Avg Stress %': '{:.1f}',
                'Avg EUR': '{:.2f}',
                'Total Operators': '{:,.0f}'
            }),
            use_container_width=True,
            hide_index=True
        )
