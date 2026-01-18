
import pandas as pd
import numpy as np
import os

# Set paths
input_path = 'master_aadhaar_data_final_cleaned.csv'
output_path = 'master_aadhaar_data_fully_cleaned.csv'

try:
    print(f"Loading {input_path}...")
    df = pd.read_csv(input_path)
    initial_rows = len(df)
    print(f"Initial row count: {initial_rows:,}")

    # 1. Drop exact duplicates
    df = df.drop_duplicates()
    after_exact_drop = len(df)
    print(f"Rows after dropping exact duplicates: {after_exact_drop:,} (Removed: {initial_rows - after_exact_drop:,})")

    # 2. Define aggregation logic
    key_columns = ['date', 'state', 'district', 'pincode', 'month_name', 'day_name', 'is_weekend']
    # List all numeric columns to be summed
    count_columns = [
        'age_0_5', 'age_5_17', 'age_18_greater', 
        'bio_age_5_17', 'bio_age_18_greater', 
        'demo_age_5_17', 'demo_age_18_greater',
        'total_enrolments', 'total_biometric_updates', 
        'total_demographic_updates', 'total_updates', 'overall_activity'
    ]

    # 3. Aggregate key duplicates by summing count columns
    print("Aggregating key-column duplicates...")
    df_aggregated = df.groupby(key_columns)[count_columns].sum().reset_index()

    # 4. Recalculate derived ratios
    print("Recalculating update_to_enrolment_ratio...")
    df_aggregated['update_to_enrolment_ratio'] = (
        df_aggregated['total_updates'] / (df_aggregated['total_enrolments'] + 0.1)
    )

    final_rows = len(df_aggregated)
    print(f"Final row count: {final_rows:,}")
    print(f"Total rows removed/consolidated: {initial_rows - final_rows:,}")

    # Verify uniqueness
    duplicate_keys = df_aggregated.duplicated(subset=['date', 'state', 'district', 'pincode']).sum()
    if duplicate_keys == 0:
        print("✓ Success: All rows are now unique by date and pincode.")
    else:
        print(f"⚠️ Warning: Still found {duplicate_keys} duplicate keys!")

    # 5. Save to a NEW file to avoid permission issues
    print(f"Saving to {output_path}...")
    df_aggregated.to_csv(output_path, index=False)
    print(f"Done! Data saved to {output_path}")

except Exception as e:
    print(f"Error occurred: {e}")
