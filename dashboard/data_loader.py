"""
Data Loader Module for Aadhaar Infrastructure Dashboard
Loads district_recommendations.csv and operator_requirements.csv
"""
import pandas as pd
import streamlit as st
from pathlib import Path


# India state centroids for fallback geocoding
STATE_CENTROIDS = {
    "Andaman and Nicobar Islands": (11.7401, 92.6586),
    "Andhra Pradesh": (15.9129, 79.7400),
    "Arunachal Pradesh": (28.2180, 94.7278),
    "Assam": (26.2006, 92.9376),
    "Bihar": (25.0961, 85.3131),
    "Chandigarh": (30.7333, 76.7794),
    "Chhattisgarh": (21.2787, 81.8661),
    "Dadra and Nagar Haveli and Daman and Diu": (20.1809, 73.0169),
    "Delhi": (28.7041, 77.1025),
    "Goa": (15.2993, 74.1240),
    "Gujarat": (22.2587, 71.1924),
    "Haryana": (29.0588, 76.0856),
    "Himachal Pradesh": (31.1048, 77.1734),
    "Jammu and Kashmir": (33.7782, 76.5762),
    "Jharkhand": (23.6102, 85.2799),
    "Karnataka": (15.3173, 75.7139),
    "Kerala": (10.8505, 76.2711),
    "Ladakh": (34.1526, 77.5771),
    "Lakshadweep": (10.5667, 72.6417),
    "Madhya Pradesh": (22.9734, 78.6569),
    "Maharashtra": (19.7515, 75.7139),
    "Manipur": (24.6637, 93.9063),
    "Meghalaya": (25.4670, 91.3662),
    "Mizoram": (23.1645, 92.9376),
    "Nagaland": (26.1584, 94.5624),
    "Odisha": (20.9517, 85.0985),
    "Puducherry": (11.9416, 79.8083),
    "Punjab": (31.1471, 75.3412),
    "Rajasthan": (27.0238, 74.2179),
    "Sikkim": (27.5330, 88.5122),
    "Tamil Nadu": (11.1271, 78.6569),
    "Telangana": (18.1124, 79.0193),
    "Tripura": (23.9408, 91.9882),
    "Uttar Pradesh": (26.8467, 80.9462),
    "Uttarakhand": (30.0668, 79.0193),
    "West Bengal": (22.9868, 87.8550),
}


@st.cache_data
def load_intervention_data():
    """Load and merge district recommendations with operator requirements."""
    base_path = Path(__file__).parent.parent
    
    # Load district recommendations (primary data)
    rec_path = base_path / "district_recommendations.csv"
    df = pd.read_csv(rec_path)
    
    # Load operator requirements (merge data)
    op_path = base_path / "operator_requirements.csv"
    op_df = pd.read_csv(op_path)
    
    # Clean up whitespace in column names
    df.columns = df.columns.str.strip()
    op_df.columns = op_df.columns.str.strip()
    
    # Merge operator data (only add columns not already present)
    merge_cols = ['state', 'district', 'operators_needed', 'stress_percentile']
    op_subset = op_df[merge_cols].drop_duplicates()
    
    # Merge on state and district
    df = df.merge(op_subset, on=['state', 'district'], how='left', suffixes=('', '_op'))
    
    # Fill missing operators with 0
    if 'operators_needed' in df.columns:
        df['operators_needed'] = df['operators_needed'].fillna(0).astype(int)
    
    # Ensure numeric columns
    numeric_cols = ['eur_mean', 'eur_std', 'total_enrolments', 'total_updates', 
                    'avg_daily_enrolments', 'avg_daily_updates', 'daily_gap',
                    'operators_needed', 'stress_percentile', 'stability_score',
                    'total_activity', 'capacity_gap']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Add synthetic lat/lon based on state centroids (for heatmap)
    df = add_geocoding(df)
    
    # Create eur_category from recommendation for compatibility
    df['eur_category'] = df['recommendation'].apply(categorize_recommendation)
    
    return df


def add_geocoding(df):
    """Add approximate lat/lon based on state centroids with small jitter for districts."""
    import numpy as np
    
    df = df.copy()
    
    def get_coords(row):
        state = row['state']
        if state in STATE_CENTROIDS:
            lat, lon = STATE_CENTROIDS[state]
            # Add small random jitter so districts don't overlap
            jitter_lat = np.random.uniform(-0.5, 0.5)
            jitter_lon = np.random.uniform(-0.5, 0.5)
            return lat + jitter_lat, lon + jitter_lon
        return None, None
    
    coords = df.apply(get_coords, axis=1)
    df['lat'] = [c[0] for c in coords]
    df['lon'] = [c[1] for c in coords]
    
    return df


def categorize_recommendation(rec):
    """Map recommendation to stress category for color coding."""
    if rec in ['Mobile Aadhaar Van', 'Permanent Centre']:
        return 'Critical'
    elif rec in ['Extra Counters', 'Semi-Permanent Support', 'Temporary Mobile Camp']:
        return 'Warning'
    else:
        return 'Normal'


def get_filtered_data(df, state=None, district=None, category=None):
    """Filter data by state, district, or stress category."""
    filtered = df.copy()
    
    if state and state != "All States":
        filtered = filtered[filtered['state'] == state]
    
    if district and district != "All Districts":
        filtered = filtered[filtered['district'] == district]
    
    if category and category != "All Categories":
        filtered = filtered[filtered['eur_category'] == category]
    
    return filtered


def get_state_list(df):
    """Get unique sorted list of states."""
    return ["All States"] + sorted(df['state'].unique().tolist())


def get_district_list(df, state=None):
    """Get unique sorted list of districts, optionally filtered by state."""
    if state and state != "All States":
        districts = df[df['state'] == state]['district'].unique()
    else:
        districts = df['district'].unique()
    return ["All Districts"] + sorted(districts.tolist())


def get_category_list():
    """Get stress category options."""
    return ["All Categories", "Critical", "Warning", "Normal"]


def get_window_class_list():
    """Get window class options for time-based filtering."""
    return ["All Windows", "short_term", "mid_term", "long_term"]


def aggregate_by_state(df):
    """Aggregate district-level data to state level."""
    agg_df = df.groupby('state').agg({
        'eur_mean': 'mean',
        'eur_std': 'mean',
        'total_enrolments': 'sum',
        'total_updates': 'sum',
        'operators_needed': 'sum',
        'daily_gap': 'sum',
        'district': 'count'
    }).reset_index()
    
    agg_df = agg_df.rename(columns={'district': 'district_count'})
    return agg_df
