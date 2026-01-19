import pandas as pd
import numpy as np
import os

def clean_data():
    input_file = 'master_aadhaar_data_cleaned.csv'
    output_file = 'master_aadhaar_data_final_cleaned.csv'
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return

    print(f"Loading {input_file}...")
    df = pd.read_csv(input_file)
    initial_shape = df.shape
    
    # 1. Remove duplicate rows
    print("Removing duplicate rows...")
    df = df.drop_duplicates()
    rows_after_duplicates = df.shape[0]
    duplicates_removed = initial_shape[0] - rows_after_duplicates
    
    # 2. Drop rows with invalid '100000' state/district/pincode
    print("Dropping invalid '100000' rows...")
    df = df[df['state'] != '100000']
    
    # 3. State Name Standardization Mapping
    state_mapping = {
        # Case and whitespace
        'andaman and Nicobar Islands': 'Andaman and Nicobar Islands',
        'andhra Pradesh': 'Andhra Pradesh',
        
        # Spelling variations
        'Chhatisgarh': 'Chhattisgarh',
        'Orissa': 'Odisha',
        'Tamilnadu': 'Tamil Nadu',
        'West Bangal': 'West Bengal',
        'West Bengli': 'West Bengal',
        'Westbengal': 'West Bengal',
        
        # Old/Alternate names
        'Uttaranchal': 'Uttarakhand',
        
        # Union Territory Consolidation
        'Dadra & Nagar Haveli': 'Dadra and Nagar Haveli and Daman and Diu',
        'Dadra and Nagar Haveli': 'Dadra and Nagar Haveli and Daman and Diu',
        'Daman & Diu': 'Dadra and Nagar Haveli and Daman and Diu',
        'Daman and Diu': 'Dadra and Nagar Haveli and Daman and Diu',
        'The Dadra and Nagar Haveli and Daman and Diu': 'Dadra and Nagar Haveli and Daman and Diu',
        'Pondicherry': 'Puducherry',
        
        # District names misclassified as states
        'Balanagar': 'Telangana',
        'Darbhanga': 'Bihar',
        'Jaipur': 'Rajasthan',
        'Madanapalle': 'Andhra Pradesh',
        'Nagpur': 'Maharashtra',
        'Puttenahalli': 'Karnataka',
        'Raja Annamalai Puram': 'Tamil Nadu'
    }
    
    print("Standardizing state names...")
    df['state'] = df['state'].replace(state_mapping)
    
    # Trim whitespace
    df['state'] = df['state'].str.strip()
    
    # Final check on state count
    unique_states = sorted(df['state'].unique())
    num_unique_states = len(unique_states)
    
    # 4. Standardize District names (Title Case)
    print("Standardizing district names to title case...")
    df['district'] = df['district'].str.title().str.strip()
    
    # 5. Ensure numeric columns are integers where appropriate
    int_cols = [
        'age_0_5', 'age_5_17', 'age_18_greater', 
        'bio_age_5_17', 'bio_age_18_greater', 
        'demo_age_5_17', 'demo_age_18_greater',
        'total_enrolments', 'total_biometric_updates', 
        'total_demographic_updates', 'total_updates', 
        'overall_activity', 'is_weekend', 'pincode'
    ]
    for col in int_cols:
        if col in df.columns:
            # First handle potential NaNs if any were introduced or existed
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
    # 6. Save the cleaned data
    print(f"Saving cleaned data to {output_file}...")
    df.to_csv(output_file, index=False)
    
    # 7. Generate Summary Report
    final_shape = df.shape
    with open('cleaning_summary_report_v2.txt', 'w') as f:
        f.write("DATA CLEANING SUMMARY REPORT\n")
        f.write("="*40 + "\n")
        f.write(f"Initial row count: {initial_shape[0]:,}\n")
        f.write(f"Duplicate rows removed: {duplicates_removed:,}\n")
        f.write(f"Invalid '100000' rows removed: {rows_after_duplicates - final_shape[0]:,}\n")
        f.write(f"Final row count: {final_shape[0]:,}\n")
        f.write(f"Total rows dropped: {initial_shape[0] - final_shape[0]:,}\n")
        f.write("\n")
        f.write(f"Unique states after cleaning: {num_unique_states}\n")
        f.write("List of states:\n")
        for i, s in enumerate(unique_states, 1):
            f.write(f"{i:2}. {s}\n")
        f.write("\n")
        f.write("Columns processed: " + ", ".join(df.columns) + "\n")

    print("\nCleaning complete!")
    print(f"Final shape: {final_shape}")
    print(f"Unique states: {num_unique_states}")
    print("Summary saved to cleaning_summary_report_v2.txt")

if __name__ == "__main__":
    clean_data()
