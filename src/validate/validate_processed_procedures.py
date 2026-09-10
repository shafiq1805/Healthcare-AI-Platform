import os
import sys
import pandas as pd


def validate_processed_procedures():
    processed_proc_path = r'data/processed/claim_procedures_processed.csv'
    processed_claims_path = r'data/processed/claims_processed.csv'

    for path in [processed_proc_path, processed_claims_path]:
        if not os.path.exists(path):
            print(f"Error: File not found at {path}")
            sys.exit(1)

    df_proc = pd.read_csv(processed_proc_path)
    df_claims = pd.read_csv(processed_claims_path)

    total_procedures = len(df_proc)

    # 1. Duplicate procedure IDs
    duplicate_proc_ids = df_proc.duplicated(subset=['claim_procedure_id']).sum()

    # 2. Invalid claim references
    valid_claim_ids = set(df_claims['claim_id'].dropna().unique())
    invalid_claim_refs = (~df_proc['claim_id'].isin(valid_claim_ids)).sum()

    # 3. Missing required fields
    required_cols = [
        'claim_procedure_id',
        'claim_id',
        'procedure_code',
        'procedure_type',
        'service_date',
        'units',
        'line_charge',
    ]
    missing_fields_count = df_proc[required_cols].isna().any(axis=1).sum()

    # 4. Invalid procedure types
    allowed_types = ['CPT', 'HCPCS']
    invalid_proc_types = (~df_proc['procedure_type'].isin(allowed_types)).sum()

    # 5. Invalid units (units < 1 or non-numeric)
    units_numeric = pd.to_numeric(df_proc['units'], errors='coerce')
    invalid_units_count = (units_numeric.isna() | (units_numeric < 1)).sum()

    # 6. Invalid line charges (line_charge < 0 or non-numeric)
    charges_numeric = pd.to_numeric(df_proc['line_charge'], errors='coerce')
    invalid_charges_count = (charges_numeric.isna() | (charges_numeric < 0)).sum()

    # 7. Invalid service dates
    parsed_dates = pd.to_datetime(df_proc['service_date'], errors='coerce')
    invalid_dates_count = parsed_dates.isna().sum()

    # 8. Business Rule: SUM(procedure line charges) <= claim.total_charge
    proc_totals = (
        df_proc.groupby('claim_id')['line_charge']
        .sum()
        .reset_index()
        .rename(columns={'line_charge': 'total_proc_charge'})
    )

    claims_merged = pd.merge(
        df_claims[['claim_id', 'total_charge']],
        proc_totals,
        on='claim_id',
        how='inner',
    )

    # Allow a small float comparison tolerance ($0.01)
    exceeded_claims = (
        claims_merged['total_proc_charge'] > (claims_merged['total_charge'] + 0.01)
    ).sum()

    # Determine Overall Validation Status
    all_passed = all(
        [
            duplicate_proc_ids == 0,
            invalid_claim_refs == 0,
            missing_fields_count == 0,
            invalid_proc_types == 0,
            invalid_units_count == 0,
            invalid_charges_count == 0,
            invalid_dates_count == 0,
            exceeded_claims == 0,
        ]
    )

    status = "PASS" if all_passed else "FAIL"

    # Print Quality Audit Report
    print("========== PROCESSED PROCEDURE VALIDATION ==========")
    print()
    print(f"Total procedures: {total_procedures}")
    print()
    print(f"Duplicate procedure IDs: {duplicate_proc_ids}")
    print(f"Invalid claim references: {invalid_claim_refs}")
    print(f"Missing required fields: {missing_fields_count}")
    print(f"Invalid procedure types: {invalid_proc_types}")
    print(f"Invalid units: {invalid_units_count}")
    print(f"Invalid line charges: {invalid_charges_count}")
    print(f"Invalid service dates: {invalid_dates_count}")
    print()
    print(f"Claims where procedure charges exceed claim charge: {exceeded_claims}")
    print()
    print("====================================================")
    print(f"STATUS: {status}")


if __name__ == '__main__':
    validate_processed_procedures()
