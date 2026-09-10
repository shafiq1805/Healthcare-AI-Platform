import os
import re
import numpy as np
import pandas as pd


def process_patients(input_path, output_path):
    df = pd.read_csv(input_path)
    raw_rows = len(df)

    # 1. Standardize column names
    df.columns = df.columns.str.strip().str.lower()

    # 2. Standardize DOB (invalid dates become NaT)
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce')

    # 3. Standardize gender: Convert invalid values (not M or F) to NaN/NULL
    allowed_genders = ['M', 'F']
    df['gender'] = df['gender'].apply(
        lambda g: (
            g.strip().upper()
            if pd.notna(g) and g.strip().upper() in allowed_genders
            else np.nan
        )
    )

    # 4. Standardize email: Convert invalid email formats to NaN/NULL
    email_pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'

    def clean_email(val):
        if pd.isna(val) or str(val).strip() == '':
            return np.nan
        cleaned = str(val).strip().lower()
        if re.match(email_pattern, cleaned):
            return cleaned
        return np.nan  # Set invalid emails like liam.oconnor.at.mail.com to NaN

    df['email'] = df['email'].apply(clean_email)

    # 5. Standardize phone
    df['phone'] = df['phone'].apply(
        lambda p: p.strip() if pd.notna(p) and str(p).strip() != '' else np.nan
    )

    # 6. Deduplicate patient_id records
    df = df.drop_duplicates(subset=['patient_id'], keep='first')
    duplicates_removed = raw_rows - len(df)

    # 7. Write the result
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print('Processing complete!')
    print(f'Raw records: {raw_rows}')
    print(f'Processed records: {len(df)}')
    print(f'Duplicates removed: {duplicates_removed}')


if __name__ == '__main__':
    input_file = (
        r'D:\App development\Healthcare AI Platform\data\raw\patients.csv'
    )
    output_file = r'D:\App development\Healthcare AI Platform\data\processed\patients_processed.csv'

    process_patients(input_file, output_file)
