import os
import pandas as pd


def transform_procedures():
    raw_proc_path = r'data/raw/claim_procedures.csv'
    processed_claims_path = r'data/processed/claims_processed.csv'
    output_processed_path = r'data/processed/claim_procedures_processed.csv'
    output_quarantine_path = (
        r'data/quarantine/claim_procedures_quarantine.csv'
    )

    # Ensure output directories exist
    os.makedirs(os.path.dirname(output_processed_path), exist_ok=True)
    os.makedirs(os.path.dirname(output_quarantine_path), exist_ok=True)

    # 1. Load Datasets
    df_raw = pd.read_csv(raw_proc_path)
    df_claims = pd.read_csv(processed_claims_path)

    raw_count = len(df_raw)
    valid_claim_ids = set(df_claims['claim_id'].dropna().unique())

    # Rule 1: Deduplicate claim_procedure_id (keep first)
    df_dedup = df_raw.drop_duplicates(
        subset=['claim_procedure_id'], keep='first'
    ).copy()
    duplicate_count = raw_count - len(df_dedup)
    unique_count = len(df_dedup)

    processed_rows = []
    quarantine_rows = []

    # Reason Counter (Counts failure flags across all records)
    quarantine_reasons_count = {
        'INVALID_CLAIM_REFERENCE': 0,
        'MISSING_LINE_CHARGE': 0,
        'INVALID_PROCEDURE_TYPE': 0,
        'NEGATIVE_UNITS': 0,
    }

    allowed_types = ['CPT', 'HCPCS']

    # 2. Process Business Rules & Multi-Issue Tracking
    for _, row in df_dedup.iterrows():
        proc_dict = row.to_dict()
        record_reasons = []

        # Check 1: Invalid Claim Reference (FK check against claims_processed)
        if proc_dict['claim_id'] not in valid_claim_ids:
            record_reasons.append('INVALID_CLAIM_REFERENCE')
            quarantine_reasons_count['INVALID_CLAIM_REFERENCE'] += 1

        # Check 2: Invalid Procedure Type
        if proc_dict['procedure_type'] not in allowed_types:
            record_reasons.append('INVALID_PROCEDURE_TYPE')
            quarantine_reasons_count['INVALID_PROCEDURE_TYPE'] += 1

        # Check 3: Missing Line Charge
        if (
            pd.isna(proc_dict['line_charge'])
            or str(proc_dict['line_charge']).strip() == ''
        ):
            record_reasons.append('MISSING_LINE_CHARGE')
            quarantine_reasons_count['MISSING_LINE_CHARGE'] += 1

        # Check 4: Invalid Units (units < 1 or missing/non-numeric)
        try:
            units_val = float(proc_dict['units'])
            if units_val < 1:
                record_reasons.append('NEGATIVE_UNITS')
                quarantine_reasons_count['NEGATIVE_UNITS'] += 1
        except (ValueError, TypeError):
            record_reasons.append('NEGATIVE_UNITS')
            quarantine_reasons_count['NEGATIVE_UNITS'] += 1

        # Decision: Route to Quarantine if ANY rule failed; otherwise to Processed
        if record_reasons:
            proc_dict['quarantine_reason'] = ';'.join(record_reasons)
            quarantine_rows.append(proc_dict)
        else:
            # Parse service_date cleanly for downstream loading
            parsed_date = pd.to_datetime(
                proc_dict['service_date'], errors='coerce'
            )
            proc_dict['service_date'] = (
                parsed_date.strftime('%Y-%m-%d')
                if pd.notna(parsed_date)
                else proc_dict['service_date']
            )
            processed_rows.append(proc_dict)

    # 3. Create DataFrames & Save CSVs
    df_processed = pd.DataFrame(processed_rows)
    df_quarantine = pd.DataFrame(quarantine_rows)

    df_processed.to_csv(output_processed_path, index=False)
    df_quarantine.to_csv(output_quarantine_path, index=False)

    # 4. Print Pipeline Audit Summary
    print('========== PROCEDURE TRANSFORMATION ==========')
    print()
    print(f'Raw records: {raw_count}')
    print(f'Duplicate records: {duplicate_count}')
    print(f'Unique records: {unique_count}')
    print()
    print(f'Quarantined procedures: {len(df_quarantine)}')
    print(f'Processed procedures: {len(df_processed)}')
    print()
    print('Quarantine reasons:')
    print(
        f"Invalid claim reference: {quarantine_reasons_count['INVALID_CLAIM_REFERENCE']}"
    )
    print(
        f"Missing line charge: {quarantine_reasons_count['MISSING_LINE_CHARGE']}"
    )
    print(
        f"Invalid procedure type: {quarantine_reasons_count['INVALID_PROCEDURE_TYPE']}"
    )
    print(f"Negative units: {quarantine_reasons_count['NEGATIVE_UNITS']}")
    print()
    print('===============================================')


if __name__ == '__main__':
    transform_procedures()
