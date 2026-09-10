import os
import pandas as pd

def transform_diagnoses():
    raw_dx_path = r'D:\App development\Healthcare AI Platform\data\raw\claim_diagnoses.csv'
    processed_claims_path = r'D:\App development\Healthcare AI Platform\data\processed\claims_processed.csv'
    output_processed_path = r'D:\App development\Healthcare AI Platform\data\processed\claim_diagnoses_processed.csv'
    output_quarantine_path = r'D:\App development\Healthcare AI Platform\data\quarantine\claim_diagnoses_quarantine.csv'

    # Ensure output directories exist
    os.makedirs(os.path.dirname(output_processed_path), exist_ok=True)
    os.makedirs(os.path.dirname(output_quarantine_path), exist_ok=True)

    # 1. Load Datasets
    df_raw = pd.read_csv(raw_dx_path)
    df_claims = pd.read_csv(processed_claims_path)

    raw_count = len(df_raw)
    valid_claims_ids = set(df_claims['claim_id'].dropna().unique())

    # Rule 1: Deduplicate claim_diagnosis_id (keep first)
    df_dedup = df_raw.drop_duplicates(
        subset='claim_diagnosis_id', keep='first'
    ).copy()

    duplicate_count = raw_count - len(df_dedup)
    unique_count = len(df_dedup)

    processed_rows = []
    quarantine_rows = []

    quarantine_reasons_count = {
        'INVALID_CLAIM_REFERENCE': 0,
        'MISSING_DIAGNOSIS_CODE': 0,
        'INVALID_DIAGNOSIS_TYPE': 0,
    }

    allowed_types = ['PRIMARY', 'SECONDARY', 'ADMITTING']

    # 2. Process Business Rules & Quarantine Logic
    for _, row in df_dedup.iterrows():
        dx_dict = row.to_dict()

        # Rule 2: Invalid Claim Reference (FK check against claims_processed)
        if dx_dict['claim_id'] not in valid_claims_ids:
            dx_dict['quarantine_reason'] = 'INVALID_CLAIM_REFERENCE'
            quarantine_rows.append(dx_dict)
            quarantine_reasons_count['INVALID_CLAIM_REFERENCE'] += 1
            continue

        # Rule 3: Missing Diagnosis Code
        if (
            pd.isna(dx_dict['diagnosis_code'])
            or str(dx_dict['diagnosis_code']).strip() == ''
        ):
            dx_dict['quarantine_reason'] = 'MISSING_DIAGNOSIS_CODE'
            quarantine_rows.append(dx_dict)
            quarantine_reasons_count['MISSING_DIAGNOSIS_CODE'] += 1
            continue

        # Rule 4: Invalid Diagnosis Type
        if dx_dict['diagnosis_type'] not in allowed_types:
            dx_dict['quarantine_reason'] = 'INVALID_DIAGNOSIS_TYPE'
            quarantine_rows.append(dx_dict)
            quarantine_reasons_count['INVALID_DIAGNOSIS_TYPE'] += 1
            continue

        processed_rows.append(dx_dict)

    # 3. Create DataFrames & Save CSVs
    df_processed = pd.DataFrame(processed_rows)
    df_quarantine = pd.DataFrame(quarantine_rows)

    df_processed.to_csv(output_processed_path, index=False)
    df_quarantine.to_csv(output_quarantine_path, index=False)

    # 4. Print Pipeline Audit Summary
    print('========== DIAGNOSIS TRANSFORMATION ==========')
    print()
    print(f'Raw records: {raw_count}')
    print(f'Duplicate records: {duplicate_count}')
    print(f'Unique records: {unique_count}')
    print()
    print(f'Quarantined diagnoses: {len(df_quarantine)}')
    print(f'Processed diagnoses: {len(df_processed)}')
    print()
    print('Quarantine reasons:')
    print(
        f"Invalid claim reference: {quarantine_reasons_count['INVALID_CLAIM_REFERENCE']}"
    )
    print(
        f"Missing diagnosis code: {quarantine_reasons_count['MISSING_DIAGNOSIS_CODE']}"
    )
    print(
        f"Invalid diagnosis type: {quarantine_reasons_count['INVALID_DIAGNOSIS_TYPE']}"
    )
    print()
    print('==============================================')


if __name__ == '__main__':

    transform_diagnoses()
