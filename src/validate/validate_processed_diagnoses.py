import os
import pandas as pd


def validate_processed_diagnoses():
    processed_dx_path = r'data/processed/claim_diagnoses_processed.csv'
    processed_claims_path = r'data/processed/claims_processed.csv'
    quarantine_dx_path = r'data/quarantine/claim_diagnoses_quarantine.csv'

    # Verify required files exist
    for path in [processed_dx_path, processed_claims_path, quarantine_dx_path]:
        if not os.path.exists(path):
            print(f'Error: File not found at {path}')
            return

    df_dx = pd.read_csv(processed_dx_path)
    df_claims = pd.read_csv(processed_claims_path)
    df_quarantine = pd.read_csv(quarantine_dx_path)

    total_diagnoses = len(df_dx)
    valid_claim_ids = set(df_claims['claim_id'].dropna().unique())

    # 1. No duplicate diagnosis IDs
    dup_count = df_dx.duplicated(subset=['claim_diagnosis_id']).sum()

    # 2. Every claim exists in processed claims
    invalid_claim_refs = (~df_dx['claim_id'].isin(valid_claim_ids)).sum()

    # 3. Diagnosis codes aren't missing
    missing_dx_codes = (
        df_dx['diagnosis_code'].isna()
        | (df_dx['diagnosis_code'].astype(str).str.strip() == '')
    ).sum()

    # 4. Diagnosis types are valid
    allowed_types = ['PRIMARY', 'SECONDARY', 'ADMITTING']
    invalid_dx_types = (~df_dx['diagnosis_type'].isin(allowed_types)).sum()

    # 5. Sequence numbers are valid (>= 1)
    invalid_seq_numbers = (
        pd.to_numeric(df_dx['sequence_num'], errors='coerce') < 1
    ).sum()

    # 6. Business Rule: At most one PRIMARY diagnosis per claim
    primary_mask = df_dx['diagnosis_type'] == 'PRIMARY'
    primary_counts = df_dx[primary_mask].groupby('claim_id').size()
    multiple_primary_claims = (primary_counts > 1).sum()

    # Overall Validation Status Check
    passed = all(
        [
            dup_count == 0,
            invalid_claim_refs == 0,
            missing_dx_codes == 0,
            invalid_dx_types == 0,
            invalid_seq_numbers == 0,
            multiple_primary_claims == 0,
        ]
    )

    # Output Validation Report
    print('========== PROCESSED DIAGNOSIS VALIDATION ==========')
    print()
    print(f'Total diagnoses: {total_diagnoses}')
    print()
    print(f'Duplicate diagnosis IDs: {dup_count}')
    print(f'Invalid claim references: {invalid_claim_refs}')
    print(f'Missing diagnosis codes: {missing_dx_codes}')
    print(f'Invalid diagnosis types: {invalid_dx_types}')
    print(f'Invalid sequence numbers: {invalid_seq_numbers}')
    print(f'Claims with multiple PRIMARY diagnoses: {multiple_primary_claims}')
    print()
    print('====================================================')
    print(f"STATUS: {'PASS' if passed else 'FAIL'}")
    print()

    # Quarantine Audit Summary
    print('========== QUARANTINE AUDIT REPORT ==========')
    print(f'Quarantined records: {len(df_quarantine)}')
    print()
    print('claim_diagnosis_id | claim_id | quarantine_reason')
    print('----------------------------------------------------')
    for _, row in df_quarantine.iterrows():
        print(
            f"{row['claim_diagnosis_id']} | {row['claim_id']} | {row['quarantine_reason']}"
        )
    print('====================================================')


if __name__ == '__main__':
    validate_processed_diagnoses()
