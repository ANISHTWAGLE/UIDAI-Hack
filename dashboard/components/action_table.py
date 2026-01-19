"""
Action Plan Table Component
Executive output table for direct administrative use.
"""
import streamlit as st
import pandas as pd


def get_action_color(action):
    """Return color for action type."""
    colors = {
        'Mobile Aadhaar Van': '#DC2626',
        'Permanent Centre': '#991B1B',
        'Extra Counters': '#F59E0B',
        'Semi-Permanent Support': '#FBBF24',
        'Temporary Mobile Camp': '#EF4444',
        'Monitor Closely': '#84CC16',
        'Monitor / No Action': '#10B981'
    }
    return colors.get(action, '#6B7280')


def get_category_color(category):
    """Return color for stress category."""
    colors = {
        'Critical': '#FEE2E2',
        'Warning': '#FEF3C7',
        'Normal': '#D1FAE5'
    }
    return colors.get(category, '#F3F4F6')


def render_action_table(df):
    """Render the action plan table component."""
    st.subheader("📋 Action Plan Table")
    
    st.markdown("""
    **Executive Output** — Directly usable by administrators.
    - Sorted by stress severity (highest first)
    - Excludes "Monitor / No Action" by default
    - Exportable to CSV
    """)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        exclude_no_action = st.checkbox("Exclude 'No Action'", value=True)
    
    with col2:
        selected_state = st.selectbox(
            "Filter by State",
            options=["All States"] + sorted(df['state'].unique().tolist()),
            key="action_table_state"
        )
    
    with col3:
        min_operators = st.number_input(
            "Min Operators Needed",
            min_value=0,
            max_value=int(df['operators_needed'].max()) if 'operators_needed' in df.columns else 100,
            value=0
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if exclude_no_action:
        filtered_df = filtered_df[filtered_df['recommendation'] != 'Monitor / No Action']
    
    if selected_state != "All States":
        filtered_df = filtered_df[filtered_df['state'] == selected_state]
    
    if 'operators_needed' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['operators_needed'] >= min_operators]
    
    # Sort by stress percentile (descending)
    if 'stress_percentile' in filtered_df.columns:
        filtered_df = filtered_df.sort_values('stress_percentile', ascending=False)
    
    # Summary metrics
    st.markdown("---")
    st.markdown("### 📊 Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Districts Shown", len(filtered_df))
    
    with col2:
        if 'operators_needed' in filtered_df.columns:
            total_operators = filtered_df['operators_needed'].sum()
            st.metric("Total Operators", f"{total_operators:,.0f}")
    
    with col3:
        critical = len(filtered_df[filtered_df['eur_category'] == 'Critical'])
        st.metric("🔴 Critical", critical)
    
    with col4:
        warning = len(filtered_df[filtered_df['eur_category'] == 'Warning'])
        st.metric("🟡 Warning", warning)
    
    st.markdown("---")
    
    # Prepare display dataframe
    display_cols = ['state', 'district', 'eur_mean', 'stress_percentile', 
                    'operators_needed', 'recommendation', 'reason']
    available_cols = [c for c in display_cols if c in filtered_df.columns]
    
    display_df = filtered_df[available_cols].copy()
    display_df.columns = [c.replace('_', ' ').title() for c in available_cols]
    
    # Display table with styling
    st.dataframe(
        display_df.style.format({
            'Eur Mean': '{:.2f}',
            'Stress Percentile': '{:.1f}%'
        }).map(
            lambda x: f'background-color: #FEE2E2; color: #991B1B;' if x == 'Mobile Aadhaar Van' or x == 'Permanent Centre' else 
                      f'background-color: #FEF3C7; color: #92400E;' if x == 'Extra Counters' else '',
            subset=['Recommendation'] if 'Recommendation' in display_df.columns else []
        ),
        use_container_width=True,
        hide_index=True,
        height=min(400, len(display_df) * 35 + 50)
    )
    
    # Export button
    st.markdown("---")
    
    csv_data = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Action Plan (CSV)",
        data=csv_data,
        file_name="aadhaar_action_plan.csv",
        mime="text/csv"
    )
    
    # State-level summary
    if st.checkbox("Show State Summary", value=False):
        st.markdown("### 📊 State-Level Summary")
        
        state_summary = filtered_df.groupby('state').agg({
            'district': 'count',
            'operators_needed': 'sum',
            'stress_percentile': 'mean'
        }).reset_index()
        state_summary.columns = ['State', 'Districts', 'Total Operators', 'Avg Stress %']
        state_summary = state_summary.sort_values('Total Operators', ascending=False)
        
        st.dataframe(
            state_summary.style.format({
                'Avg Stress %': '{:.1f}%',
                'Total Operators': '{:,.0f}'
            }),
            use_container_width=True,
            hide_index=True
        )
