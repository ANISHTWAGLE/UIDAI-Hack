"""
Data Preprocessing Script for Aadhaar Master Dataset
This script loads, cleans, and merges Enrolment, Biometric, and Demographic data.
"""

import pandas as pd
import glob
import os
from datetime import datetime

def load_category_data(pattern, category_name):
    """Load, deduplicate, and standardize a specific category of data"""
    files = glob.glob(pattern)
    print(f"\nLoading {category_name} ({len(files)} files)...")
    if not files:
        print(f"  ⚠ No files found for {category_name}")
        return pd.DataFrame()
        
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    initial_len = len(df)
    df = df.drop_duplicates()
    print(f"  Rows: {len(df):,} (Removed {initial_len - len(df):,} duplicates)")
    
    # Standardize State names (simple version)
    df['state'] = df['state'].fillna('Unknown').str.strip().str.title()
    # Fix common variations (example)
    state_fixes = {
        'West  Bengal': 'West Bengal',
        'Andaman & Nicobar Islands': 'Andaman and Nicobar Islands',
        'Jammu & Kashmir': 'Jammu and Kashmir'
    }
    df['state'] = df['state'].replace(state_fixes)
    
    # Standardize Date
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    
    return df

def main():
    print("=" * 60)
    print("AADHAAR DATA MASTER PREPROCESSING")
    print("=" * 60)
    
    # 1. Load Data
    e_df = load_category_data('api_data_aadhar_enrolment/api_data_aadhar_enrolment/*.csv', 'Enrolment')
    b_df = load_category_data('api_data_aadhar_biometric/api_data_aadhar_biometric/*.csv', 'Biometric')
    d_df = load_category_data('api_data_aadhar_demographic/api_data_aadhar_demographic/*.csv', 'Demographic')
    
    # 2. Merge
    print("\nMerging datasets into Master View...")
    # Join on core identifiers
    master_df = pd.merge(e_df, b_df, on=['date', 'state', 'district', 'pincode'], how='outer')
    master_df = pd.merge(master_df, d_df, on=['date', 'state', 'district', 'pincode'], how='outer')
    
    # 3. Handle Counts & NaNs
    count_cols = [
        'age_0_5', 'age_5_17', 'age_18_greater', 
        'bio_age_5_17', 'bio_age_17_', 
        'demo_age_5_17', 'demo_age_17_'
    ]
    # Filter only those that exist in the dataframe
    actual_cols = [c for c in count_cols if c in master_df.columns]
    master_df[actual_cols] = master_df[actual_cols].fillna(0).astype(int)
    
    # 4. Feature Engineering
    print("Creating analysis metrics...")
    
    # Enrolment Totals
    master_df['total_enrolments'] = master_df['age_0_5'] + master_df['age_5_17'] + master_df['age_18_greater']
    
    # Update Totals
    master_df['total_biometric_updates'] = master_df['bio_age_5_17'] + master_df['bio_age_17_']
    master_df['total_demographic_updates'] = master_df['demo_age_5_17'] + master_df['demo_age_17_']
    master_df['total_updates'] = master_df['total_biometric_updates'] + master_df['total_demographic_updates']
    
    # Overall Activity
    master_df['overall_activity'] = master_df['total_enrolments'] + master_df['total_updates']
    
    # Ratio: Updates vs Enrolments
    master_df['update_to_enrolment_ratio'] = (master_df['total_updates'] / (master_df['total_enrolments'] + 0.1)).round(2)
    
    # Temporal features
    master_df['month_name'] = master_df['date'].dt.strftime('%B')
    master_df['day_name'] = master_df['date'].dt.strftime('%A')
    master_df['is_weekend'] = master_df['date'].dt.dayofweek.isin([5, 6]).astype(int)
    
    # 5. Save
    output_file = 'master_aadhaar_data.csv'
    master_df.to_csv(output_file, index=False)
    
    print("\n" + "=" * 60)
    print("PREPROCESSING COMPLETE")
    print("=" * 60)
    print(f"Master file: {output_file}")
    print(f"Total Rows: {len(master_df):,}")
    print(f"Columns: {len(master_df.columns)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
