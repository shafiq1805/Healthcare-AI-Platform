import os
import pandas as pd


def validate_procedures():
    raw_proc_path = r'data/raw/claim_procedures.csv'
    processed_claims_path = r'data/processed/claims_processed.csv'

    for path in [raw_proc_path, processed_claims_path]:
        if not os.path.exists(path):
            print(f'Error: File not found at {path}')
            return

    df_proc = pd.read_csv(raw_proc_path)
    df_claims = pd.read_csv(processed_claims_path)

    total_records = len(df_proc)
    unique_ids = df_proc['claim_procedure_id'].nunique()
    valid_claim_ids = set(df_claims['claim_id'].dropna().unique())

    # 1. Duplicate claim_procedure_id
    dup_ids = df_proc[df_proc.duplicated(subset=['claim_procedure_id'])][
        'claim_procedure_id'
    ].tolist()

    # 2. Missing required fields
    required_cols = [
        'claim_procedure_id',
        'claim_id',
        'procedure_code',
        'procedure_type',
        'service_date',
        'units',
        'line_charge',
    ]
    missing_records = []
    for _, row in df_proc.iterrows():
        missing_fields = [
            col
            for col in required_cols
            if pd.isna(row[col]) or str(row[col]).strip() == ''
        ]
        if missing_fields:
            missing_records.append(
                f"  {row['claim_procedure_id']} → missing {', '.join(missing_fields)}"
            )

    # 3. Invalid procedure types
    allowed_types = ['CPT', 'HCPCS']
    invalid_type_mask = (
        ~df_proc['procedure_type'].isin(allowed_types)
    ) & df_proc['procedure_type'].notna()
    invalid_types = [
        f"  {row['claim_procedure_id']} → {row['procedure_type']}"
        for _, row in df_proc[invalid_type_mask].iterrows()
    ]

    # 4. Invalid claim references (FK against claims_processed)
    invalid_claims_mask = ~df_proc['claim_id'].isin(valid_claim_ids)
    invalid_claims = [
        f"  {row['claim_procedure_id']} → {row['claim_id']}"
        for _, row in df_proc[invalid_claims_mask].iterrows()
    ]

    # 5. Invalid units (units < 1 or non-numeric)
    units_numeric = pd.to_numeric(df_proc['units'], errors='coerce')
    invalid_units_mask = units_numeric.isna() | (units_numeric < 1)
    invalid_units = [
        f"  {row['claim_procedure_id']} → {row['units']}"
        for _, row in df_proc[invalid_units_mask].iterrows()
    ]

    # 6. Invalid line charges (line_charge < 0 or non-numeric)
    charges_numeric = pd.to_numeric(df_proc['line_charge'], errors='coerce')
    # Filter out missing ones since they are caught under missing fields
    invalid_charges_mask = (charges_numeric < 0) & df_proc[
        'line_charge'
    ].notna()
    invalid_charges = [
        f"  {row['claim_procedure_id']} → {row['line_charge']}"
        for _, row in df_proc[invalid_charges_mask].iterrows()
    ]

    # 7. Invalid service dates
    parsed_dates = pd.to_datetime(df_proc['service_date'], errors='coerce')
    invalid_dates_mask = df_proc['service_date'].notna() & parsed_dates.isna()
    invalid_dates = [
        f"  {row['claim_procedure_id']} → {row['service_date']}"
        for _, row in df_proc[invalid_dates_mask].iterrows()
    ]

    # Output Data Quality Report
    print('========== PROCEDURE DATA QUALITY REPORT ==========')
    print()
    print(f'Total records: {total_records}')
    print(f'Unique procedure IDs: {unique_ids}')
    print()
    print('Duplicate procedure IDs:')
    print('\n'.join([f'  {pid}' for pid in dup_ids]) if dup_ids else '  None')
    print()
    print('Missing required fields:')
    print('\n'.join(missing_records) if missing_records else '  None')
    print()
    print('Invalid procedure types:')
    print('\n'.join(invalid_types) if invalid_types else '  None')
    print()
    print('Invalid claim references:')
    print('\n'.join(invalid_claims) if invalid_claims else '  None')
    print()
    print('Invalid units:')
    print('\n'.join(invalid_units) if invalid_units else '  None')
    print()
    print('Invalid line charges:')
    print('\n'.join(invalid_charges) if invalid_charges else '  None')
    print()
    print('Invalid service dates:')
    print('\n'.join(invalid_dates) if invalid_dates else '  None')
    print()
    print('===================================================')


if __name__ == '__main__':
    validate_procedures()
