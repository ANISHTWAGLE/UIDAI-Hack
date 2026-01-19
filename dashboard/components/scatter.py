"""
Decision Scatter Plot Component
Visualizes EUR mean vs stability with recommendation coloring.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# Color map for recommendations
RECOMMENDATION_COLORS = {
    'Mobile Aadhaar Van': '#DC2626',
    'Permanent Centre': '#991B1B',
    'Extra Counters': '#F59E0B',
    'Semi-Permanent Support': '#FBBF24',
    'Temporary Mobile Camp': '#EF4444',
    'Monitor Closely': '#84CC16',
    'Monitor / No Action': '#10B981'
}


def create_decision_scatter(df):
    """Create scatter plot for intervention decision matrix."""
    if 'eur_mean' not in df.columns or 'eur_std' not in df.columns:
        return None
    
    plot_df = df.dropna(subset=['eur_mean', 'eur_std']).copy()
    
    if len(plot_df) == 0:
        return None
    
    # Use total_activity for sizing if available
    size_col = 'total_activity' if 'total_activity' in plot_df.columns else None
    
    fig = px.scatter(
        plot_df,
        x='eur_mean',
        y='eur_std',
        color='recommendation',
        color_discrete_map=RECOMMENDATION_COLORS,
        size=size_col if size_col else None,
        size_max=30,
        hover_data={
            'state': True,
            'district': True,
            'eur_mean': ':.2f',
            'eur_std': ':.2f',
            'stress_percentile': ':.1f',
            'operators_needed': True,
            'recommendation': True
        },
        title="Intervention Decision Matrix: Stress Intensity vs Volatility"
    )
    
    # Add quadrant lines
    eur_mean_median = plot_df['eur_mean'].median()
    eur_std_median = plot_df['eur_std'].median()
    
    fig.add_hline(y=eur_std_median, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=eur_mean_median, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add quadrant annotations
    annotations = [
        dict(x=eur_mean_median * 0.3, y=plot_df['eur_std'].max() * 0.9,
             text="Low Stress<br>High Volatility<br>→ Monitor", showarrow=False,
             font=dict(size=10, color="#6B7280")),
        dict(x=plot_df['eur_mean'].max() * 0.8, y=plot_df['eur_std'].max() * 0.9,
             text="High Stress<br>High Volatility<br>→ Mobile Van", showarrow=False,
             font=dict(size=10, color="#DC2626")),
        dict(x=eur_mean_median * 0.3, y=plot_df['eur_std'].min() + (eur_std_median * 0.2),
             text="Low Stress<br>Low Volatility<br>→ No Action", showarrow=False,
             font=dict(size=10, color="#10B981")),
        dict(x=plot_df['eur_mean'].max() * 0.8, y=plot_df['eur_std'].min() + (eur_std_median * 0.2),
             text="High Stress<br>Low Volatility<br>→ Permanent Centre", showarrow=False,
             font=dict(size=10, color="#991B1B")),
    ]
    
    fig.update_layout(
        annotations=annotations,
        xaxis_title="EUR Mean (Stress Intensity)",
        yaxis_title="EUR Std (Volatility)",
        legend_title="Recommendation",
        height=600,
        template="plotly_white"
    )
    
    return fig


def render_scatter(df):
    """Render the decision scatter plot component."""
    st.subheader("🎯 Intervention Decision Matrix")
    
    st.markdown("""
    This scatter plot shows each district positioned by:
    - **X-axis**: EUR Mean (stress intensity - higher = more stressed)
    - **Y-axis**: EUR Std (volatility - higher = less stable)
    
    **Quadrant Logic:**
    | Stress | Volatility | Recommendation |
    |--------|------------|----------------|
    | High | High | Mobile Van (temporary) |
    | High | Low | Permanent Centre |
    | Medium | Any | Extra Counters |
    | Low | Any | Monitor / No Action |
    """)
    
    # Create and display scatter plot
    fig = create_decision_scatter(df)
    
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Insufficient data for decision scatter plot.")
        return
    
    # Action distribution summary
    st.markdown("### 📊 Action Distribution")
    
    if 'recommendation' in df.columns:
        action_counts = df['recommendation'].value_counts()
        
        fig_bar = px.bar(
            x=action_counts.values,
            y=action_counts.index,
            orientation='h',
            color=action_counts.index,
            color_discrete_map=RECOMMENDATION_COLORS,
            title="Districts by Recommended Action"
        )
        fig_bar.update_layout(
            showlegend=False,
            xaxis_title="Number of Districts",
            yaxis_title="",
            height=300
        )
        st.plotly_chart(fig_bar, use_container_width=True)
