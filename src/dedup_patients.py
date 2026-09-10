import os
import pandas as pd


def process_patients(input_path, output_path):
    # 1. Read raw data
    df = pd.read_csv(input_path)
    raw_rows = len(df)

    # 2. Standardize column names (lowercase & stripped)
    df.columns = df.columns.str.strip().str.lower()

    # 3. Standardize DOB (invalid dates become NaT)
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce')

    # 4. Standardize gender (strip whitespace and uppercase, preserving 'Unknown')
    def standardize_gender(val):
        if pd.isna(val):
            return val
        cleaned = str(val).strip()
        if cleaned.lower() == 'unknown':
            return 'Unknown'
        return cleaned.upper()

    df['gender'] = df['gender'].apply(standardize_gender)

    # 5. Standardize email (strip whitespace and convert text to lowercase)
    def standardize_email(val):
        if pd.isna(val) or str(val).strip() == '':
            return val
        return str(val).strip().lower()

    df['email'] = df['email'].apply(standardize_email)

    # 6. Standardize phone (strip whitespace, preserve missing values)
    def standardize_phone(val):
        if pd.isna(val) or str(val).strip() == '':
            return val
        return str(val).strip()

    df['phone'] = df['phone'].apply(standardize_phone)

    # 7. Deduplicate patient_id records
    df = df.drop_duplicates(subset=['patient_id'], keep='first')
    duplicates_removed = raw_rows - len(df)

    # 8. Write the result
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print('Processed dataset saved successfully...')
    print(f'Raw records: {raw_rows}')
    print(f'Total rows: {len(df)}')
    print(f'Duplicates removed: {duplicates_removed}')
    print(f'Duplicate check count: {df["patient_id"].duplicated().sum()}')


if __name__ == '__main__':
    input_file = (
        r'D:\App development\Healthcare AI Platform\data\raw\patients.csv'
    )
    output_file = r'D:\App development\Healthcare AI Platform\data\processed\patients_processed.csv'

    process_patients(input_file, output_file)
