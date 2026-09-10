import os
import pandas as pd


def validate_processed_claims():
    processed_claims_path = r'data/processed/claims_processed.csv'
    processed_patients_path = r'data/processed/patients_processed.csv'
    quarantine_claims_path = r'data/quarantine/claims_quarantine.csv'

    # Verify required files exist
    for path in [
        processed_claims_path,
        processed_patients_path,
        quarantine_claims_path,
    ]:
        if not os.path.exists(path):
            print(f'Error: File not found at {path}')
            return

    df_claims = pd.read_csv(processed_claims_path)
    df_patients = pd.read_csv(processed_patients_path)
    df_quarantine = pd.read_csv(quarantine_claims_path)

    total_claims = len(df_claims)
    valid_patient_ids = set(df_patients['patient_id'].dropna().unique())

    # 1. Duplicate claim IDs
    dup_count = df_claims.duplicated(subset=['claim_id']).sum()

    # 2. Invalid patient references
    invalid_patients = (~df_claims['patient_id'].isin(valid_patient_ids)).sum()

    # 3. Invalid claim statuses
    allowed_statuses = ['SUBMITTED', 'PAID', 'DENIED', 'PENDING']
    invalid_statuses = (~df_claims['claim_status'].isin(allowed_statuses)).sum()

    # 4. Invalid charges (total_charge <= 0)
    invalid_charges = (df_claims['total_charge'] <= 0).sum()

    # 5. Missing required fields (service_date is now mandatory)
    required_cols = [
        'claim_id',
        'patient_id',
        'service_date',
        'provider_id',
        'payer',
        'claim_status',
        'total_charge',
    ]
    missing_req = df_claims[required_cols].isnull().sum().sum()

    # 6. UNKNOWN payer records count
    unknown_payer_count = (df_claims['payer'] == 'UNKNOWN').sum()

    # Overall Status Check
    passed = all(
        [
            dup_count == 0,
            invalid_patients == 0,
            invalid_statuses == 0,
            invalid_charges == 0,
            missing_req == 0,
        ]
    )

    # Output Report
    print('========== PROCESSED CLAIM VALIDATION ==========')
    print()
    print(f'Total claims: {total_claims}')
    print()
    print(f'Duplicate claim IDs: {dup_count}')
    print(f'Invalid patient references: {invalid_patients}')
    print(f'Invalid claim statuses: {invalid_statuses}')
    print(f'Invalid charges: {invalid_charges}')
    print(f'Missing required fields: {missing_req}')
    print(f'UNKNOWN payer records: {unknown_payer_count}')
    print()
    print('===============================================')
    print(f"STATUS: {'PASS' if passed else 'FAIL'}")
    print()

    # Quarantine Audit Verification
    print('========== QUARANTINE AUDIT REPORT ==========')
    print(f'Quarantined records: {len(df_quarantine)}')
    print()
    print('claim_id | quarantine_reason')
    print('-----------------------------------------------')
    for _, row in df_quarantine.iterrows():
        print(f"{row['claim_id']} | {row['quarantine_reason']}")
    print('===============================================')


if __name__ == '__main__':
    validate_processed_claims()
