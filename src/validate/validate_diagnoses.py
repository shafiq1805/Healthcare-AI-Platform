import os
import pandas as pd

def validate_diagnoses():
    raw_dx_path = r'D:\App development\Healthcare AI Platform\data\raw\claim_diagnoses.csv'
    processed_claims_path = r'D:\App development\Healthcare AI Platform\data\processed\claims_processed.csv'

    for path in [raw_dx_path,processed_claims_path]:
        if not os.path.exists(path):
            print(f"Error: The file '{path}' does not exist.")
            return

    df_dx=pd.read_csv(raw_dx_path)
    df_claims=pd.read_csv(processed_claims_path)

    total_records = len(df_dx)
    unique_ids = df_dx['claim_diagnosis_id'].nunique()
    valid_claim_ids = set(df_claims['claim_id'].dropna().unique())

    # 1. Duplicate claim_diagnosis_id
    dup_ids = df_dx[df_dx.duplicated(subset=['claim_diagnosis_id'])]['claim_diagnosis_id'].tolist()

    # 2. Missing required fields
    required_cols = [
        'claim_diagnosis_id',
        'claim_id',
        'diagnosis_code',
        'diagnosis_type',
        'sequence_num',
    ]
    missing_records = []
    for _,row in df_dx.iterrows():
        missing_fields = [
            col for col in required_cols if pd.isna(row[col]) or str(row[col]).strip() == ''
        ]

        if missing_fields:
            missing_records.append(f"{row['claim_diagnosis_id']} (Missing: {', '.join(missing_fields)})")


    # 3. Invalid diagnosis types
    allowed_types = ['PRIMARY', 'SECONDARY', 'ADMITTING']
    invalid_type_mask = (
        ~df_dx['diagnosis_type'].isin(allowed_types)
    ) & df_dx['diagnosis_type'].notna()
    invalid_types = [
        f"  {row['claim_diagnosis_id']} → {row['diagnosis_type']}"
        for _, row in df_dx[invalid_type_mask].iterrows()
    ]

    # 4. Invalid claim references
    invalid_claims_mask = ~df_dx['claim_id'].isin(valid_claim_ids)
    invalid_claims = [
        f"  {row['claim_diagnosis_id']} → {row['claim_id']}"
        for _, row in df_dx[invalid_claims_mask].iterrows()
    ]

    # 5. Invalid sequence numbers (sequence_num < 1 or non-numeric)
    sequence_numeric = pd.to_numeric(
    df_dx['sequence_num'],
    errors='coerce'
    )

    invalid_seq_mask = (
        sequence_numeric.isna()
        |(sequence_numeric < 1)
    )

    invalid_seq_count = invalid_seq_mask.sum()


    # Output Data Quality Report
    print('========== DIAGNOSIS DATA QUALITY REPORT ==========')
    print()
    print(f'Total records: {total_records}')
    print(f'Unique diagnosis IDs: {unique_ids}')
    print()
    print('Duplicate diagnosis IDs:')
    print('\n'.join([f'  {did}' for did in dup_ids]) if dup_ids else '  None')
    print()
    print('Missing required fields:')
    print('\n'.join(missing_records) if missing_records else '  None')
    print()
    print('Invalid diagnosis types:')
    print('\n'.join(invalid_types) if invalid_types else '  None')
    print()
    print('Invalid claim references:')
    print('\n'.join(invalid_claims) if invalid_claims else '  None')
    print()
    print(f'Invalid sequence numbers: {invalid_seq_count}')
    print()
    print('====================================================')

if __name__ == "__main__":
    validate_diagnoses()
