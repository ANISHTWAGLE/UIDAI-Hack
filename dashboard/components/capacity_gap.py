"""
Capacity Gap Estimation Component
Converts stress into quantifiable staffing and budget needs.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def render_capacity_gap(df):
    """Render the capacity gap estimation component."""
    st.subheader("🧮 Capacity Gap Estimation")
    
    st.markdown("""
    **Purpose:** Convert stress metrics into actionable numbers for:
    - Staffing orders
    - Budget sanction
    - Tendering processes
    
    *The operator requirements are pre-computed in the dataset.*
    """)
    
    # Key assumptions display
    with st.expander("📖 Assumptions (Configurable)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            operator_capacity = st.number_input(
                "Transactions per operator/day",
                min_value=10, max_value=200, value=50
            )
            working_days = st.number_input(
                "Working days per month",
                min_value=15, max_value=30, value=25
            )
        with col2:
            operator_salary = st.number_input(
                "Operator salary (₹/month)",
                min_value=5000, max_value=50000, value=15000
            )
    
    st.markdown("---")
    
    # Summary metrics
    st.markdown("### 📊 Capacity Requirements Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'operators_needed' in df.columns:
            total_operators = df['operators_needed'].sum()
            st.metric("Total Operators Needed", f"{total_operators:,.0f}")
        else:
            st.metric("Total Operators Needed", "N/A")
    
    with col2:
        if 'daily_gap' in df.columns:
            total_gap = df[df['daily_gap'] > 0]['daily_gap'].sum()
            st.metric("Daily Transaction Gap", f"{total_gap:,.0f}")
        else:
            st.metric("Daily Transaction Gap", "N/A")
    
    with col3:
        if 'operators_needed' in df.columns:
            monthly_cost = total_operators * operator_salary
            st.metric("Monthly Cost (Est.)", f"₹{monthly_cost:,.0f}")
    
    with col4:
        if 'operators_needed' in df.columns:
            annual_cost = monthly_cost * 12
            st.metric("Annual Budget", f"₹{annual_cost/10000000:.2f} Cr")
    
    st.markdown("---")
    
    # Operators by state
    st.markdown("### 👥 Operators Needed by State")
    
    if 'operators_needed' in df.columns:
        state_operators = df.groupby('state')['operators_needed'].sum().reset_index()
        state_operators = state_operators[state_operators['operators_needed'] > 0]
        state_operators = state_operators.sort_values('operators_needed', ascending=True).tail(15)
        
        fig = px.bar(
            state_operators,
            y='state',
            x='operators_needed',
            orientation='h',
            color='operators_needed',
            color_continuous_scale=['#60A5FA', '#3B82F6', '#1D4ED8'],
            title="Top 15 States by Operators Required"
        )
        
        fig.update_layout(
            yaxis_title="",
            xaxis_title="Operators Needed",
            height=500,
            template="plotly_white",
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Cost by state
    st.markdown("### 💰 Budget Allocation by State")
    
    if 'operators_needed' in df.columns:
        state_costs = df.groupby('state')['operators_needed'].sum().reset_index()
        state_costs['monthly_cost'] = state_costs['operators_needed'] * operator_salary
        state_costs['annual_cost_cr'] = (state_costs['monthly_cost'] * 12) / 10000000
        state_costs = state_costs[state_costs['operators_needed'] > 0]
        state_costs = state_costs.sort_values('annual_cost_cr', ascending=False).head(15)
        
        fig = px.bar(
            state_costs,
            x='state',
            y='annual_cost_cr',
            color='annual_cost_cr',
            color_continuous_scale=['#10B981', '#F59E0B', '#DC2626'],
            title="Top 15 States: Annual Budget Required (₹ Crores)"
        )
        
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Annual Budget (₹ Crores)",
            xaxis_tickangle=45,
            height=400,
            template="plotly_white",
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # District-level detail table
    st.markdown("### 📋 District-Level Requirements")
    
    if 'operators_needed' in df.columns:
        # Only show districts that need operators
        needs_df = df[df['operators_needed'] > 0].copy()
        needs_df = needs_df.sort_values('operators_needed', ascending=False)
        
        display_cols = ['state', 'district', 'avg_daily_enrolments', 'avg_daily_updates', 
                       'daily_gap', 'operators_needed', 'recommendation']
        available_cols = [c for c in display_cols if c in needs_df.columns]
        
        display_df = needs_df[available_cols].head(50).copy()
        display_df.columns = [c.replace('_', ' ').title() for c in available_cols]
        
        st.dataframe(
            display_df.style.format({
                'Avg Daily Enrolments': '{:.1f}',
                'Avg Daily Updates': '{:.1f}',
                'Daily Gap': '{:.1f}'
            }),
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Export
        csv_data = needs_df[available_cols].to_csv(index=False)
        st.download_button(
            label="📥 Download Capacity Requirements (CSV)",
            data=csv_data,
            file_name="aadhaar_capacity_requirements.csv",
            mime="text/csv"
        )
