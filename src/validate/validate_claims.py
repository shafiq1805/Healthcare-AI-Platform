import os
import pandas as pd

def validate_claims():
    raw_claims_path=r'D:\App development\Healthcare AI Platform\data\raw\claims.csv'
    processed_patients_path = r'D:\App development\Healthcare AI Platform\data\processed\patients_processed.csv'

    if not os.path.exists(raw_claims_path):
        print(f"Error: The file '{raw_claims_path}' does not exist.")
        return

    df_claims = pd.read_csv(raw_claims_path)
    total_records = len(df_claims)
    unique_claims = df_claims['claim_id'].nunique()

    # Duplicate claim_id check
    duplicate_ids = df_claims[df_claims.duplicated(subset=['claim_id'])]['claim_id'].tolist()

    # Missing required values
    missing_counts = df_claims.isnull().sum()

    missing_report = [
    f'  {col}: {count}'
    for col, count in missing_counts.items()
    if count > 0
    ]


    # Validate service dates
    parsed_dates = pd.to_datetime(
        df_claims['service_date'],
        errors='coerce'
    )

    invalid_date_claims = df_claims[parsed_dates.isna() & df_claims['service_date'].notna()]['claim_id'].tolist()


    # 4. Invalid claim statuses
    # -------------------------------------------------------------
    allowed_statuses = ['SUBMITTED', 'PAID', 'DENIED', 'PENDING']
    invalid_status_mask = (
        ~df_claims['claim_status'].isin(allowed_statuses)
    ) & df_claims['claim_status'].notna()

    invalid_status_claims = [
    f'  {row.claim_id} → {row.claim_status}'
    for _, row in df_claims[invalid_status_mask].iterrows()
    ]

    invalid_charge_mask = (
    df_claims['total_charge'] <= 0
    ) & df_claims['total_charge'].notna()

    invalid_charge_claims = [
    f'  {row.claim_id} → {row.total_charge}'
    for _, row in df_claims[invalid_charge_mask].iterrows()
    ]


    # 6. Referential Integrity Check (patient_id ∉ patients_processed)
    # -------------------------------------------------------------
    invalid_patient_refs = []
    if os.path.exists(processed_patients_path):
        df_patients = pd.read_csv(processed_patients_path)
        valid_patient_ids = set(df_patients['patient_id'].dropna().unique())

        invalid_ref_mask = ~df_claims['patient_id'].isin(valid_patient_ids)

        invalid_patient_refs = [
            f'  {row.claim_id} → {row.patient_id}'
        for _, row in df_claims[invalid_ref_mask].iterrows()
        ]
    else:
        invalid_patient_refs = [
            '  Warning: Processed patients file not found for FK check.'
        ]

    # Print Data Quality Report
    # -------------------------------------------------------------
    print('========== CLAIM DATA QUALITY REPORT ==========')
    print()
    print(f'Total records: {total_records}')
    print(f'Unique claims: {unique_claims}')
    print()
    print('Duplicate claim IDs:')
    print(
        '\n'.join([f'  {cid}' for cid in duplicate_ids])
        if duplicate_ids
        else '  None'
    )
    print()
    print('Missing values:')
    print('\n'.join(missing_report) if missing_report else '  None')
    print()
    print('Invalid service dates:')
    print(
        '\n'.join([f'  {cid}' for cid in invalid_date_claims])
        if invalid_date_claims
        else '  None'
    )
    print()
    print('Invalid claim statuses:')
    print(
        '\n'.join(invalid_status_claims) if invalid_status_claims else '  None'
    )
    print()
    print('Invalid charges:')
    print(
        '\n'.join(invalid_charge_claims) if invalid_charge_claims else '  None'
    )
    print()
    print('Invalid patient references:')
    print(
        '\n'.join(invalid_patient_refs) if invalid_patient_refs else '  None'
    )
    print()
    print('===============================================')




if __name__ == '__main__':
    validate_claims()
