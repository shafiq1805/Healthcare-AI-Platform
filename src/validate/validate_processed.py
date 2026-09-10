import re
import pandas as pd


def validate_processed_data(file_path):
    # Load dataset while parsing date_of_birth to datetime
    df = pd.read_csv(file_path)

    # Convert date_of_birth explicitly to datetime64[ns] to verify column dtype
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce')

    # 1. Check patient_id uniqueness
    duplicate_count = df['patient_id'].duplicated().sum()

    # 2. Check invalid gender values (excluding NULL/NaN)
    invalid_genders = df[df['gender'].notna() & ~df['gender'].isin(['M', 'F'])]
    invalid_gender_count = len(invalid_genders)

    # 3. Check invalid email format (excluding NULL/NaN)
    email_pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
    invalid_emails = df[
        df['email'].notna()
        & ~df['email'].astype(str).str.match(email_pattern)
    ]
    invalid_email_count = len(invalid_emails)

    # 4. Confirm date_of_birth dtype
    dob_dtype = df['date_of_birth'].dtype

    # Overall Status evaluation
    is_dob_datetime = pd.api.types.is_datetime64_any_dtype(df['date_of_birth'])
    if (
        duplicate_count == 0
        and invalid_gender_count == 0
        and invalid_email_count == 0
        and is_dob_datetime
    ):
        status = 'PASS'
    else:
        status = 'FAIL'

    # Print Validation Report
    print('========== PROCESSED DATA VALIDATION ==========\n')
    print(f'Total records: {len(df)}\n')
    print(f'Duplicate patient IDs: {duplicate_count}\n')
    print(f'Invalid gender values: {invalid_gender_count}\n')
    print(f'Invalid email formats: {invalid_email_count}\n')
    print(f'DOB data type: {dob_dtype}\n')
    print('===============================================')
    print(f'STATUS: {status}')


if __name__ == '__main__':
    processed_file = r'D:\App development\Healthcare AI Platform\data\processed\patients_processed.csv'
    validate_processed_data(processed_file)
