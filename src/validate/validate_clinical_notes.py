import os
import pandas as pd


def validate_clinical_notes():
    raw_notes_path = r'data/raw/clinical_notes.csv'
    processed_patients_path = r'data/processed/patients_processed.csv'
    processed_claims_path = r'data/processed/claims_processed.csv'

    for path in [raw_notes_path, processed_patients_path, processed_claims_path]:
        if not os.path.exists(path):
            print(f'Error: File not found at {path}')
            return

    # Read CSV and drop rows that are completely empty
    df_notes = pd.read_csv(raw_notes_path).dropna(how='all')
    df_patients = pd.read_csv(processed_patients_path)
    df_claims = pd.read_csv(processed_claims_path)

    total_records = len(df_notes)
    unique_ids = df_notes['note_id'].dropna().nunique()
    valid_patient_ids = set(df_patients['patient_id'].dropna().unique())
    valid_claim_ids = set(df_claims['claim_id'].dropna().unique())

    # 1. Duplicate note_id
    dup_ids = df_notes[df_notes.duplicated(subset=['note_id'])][
        'note_id'
    ].dropna().unique().tolist()

    # 2. Missing required fields
    required_cols = [
        'note_id',
        'patient_id',
        'encounter_id',
        'claim_id',
        'note_type',
        'note_date',
        'author_provider_id',
        'note_text',
    ]
    missing_records = []
    for _, row in df_notes.iterrows():
        missing_fields = [
            col for col in required_cols if pd.isna(row[col]) or str(row[col]).strip() == ''
        ]
        if missing_fields:
            missing_records.append(
                f"  {row['note_id']} → missing {', '.join(missing_fields)}"
            )

    # 3. Invalid note types
    allowed_types = ['SOAP', 'PROGRESS', 'DISCHARGE', 'OPERATIVE']
    invalid_type_mask = (
        ~df_notes['note_type'].isin(allowed_types)
    ) & df_notes['note_type'].notna()
    invalid_types = [
        f"  {row['note_id']} → {row['note_type']}"
        for _, row in df_notes[invalid_type_mask].iterrows()
    ]

    # 4. Invalid patient references
    invalid_patients_mask = (~df_notes['patient_id'].isin(valid_patient_ids)) & df_notes['patient_id'].notna()
    invalid_patients = [
        f"  {row['note_id']} → {row['patient_id']}"
        for _, row in df_notes[invalid_patients_mask].iterrows()
    ]

    # 5. Invalid claim references
    invalid_claims_mask = (~df_notes['claim_id'].isin(valid_claim_ids)) & df_notes['claim_id'].notna()
    invalid_claims = [
        f"  {row['note_id']} → {row['claim_id']}"
        for _, row in df_notes[invalid_claims_mask].iterrows()
    ]

    # 6. Invalid dates
    parsed_dates = pd.to_datetime(df_notes['note_date'], errors='coerce')
    invalid_dates_mask = df_notes['note_date'].notna() & parsed_dates.isna()
    invalid_dates = [
        f"  {row['note_id']} → {row['note_date']}"
        for _, row in df_notes[invalid_dates_mask].iterrows()
    ]

    # Output Data Quality Report
    print('========== CLINICAL NOTES DATA QUALITY REPORT ==========')
    print()
    print(f'Total records: {total_records}')
    print(f'Unique note IDs: {unique_ids}')
    print()
    print('Duplicate note IDs:')
    print('\n'.join([f'  {nid}' for nid in dup_ids]) if dup_ids else '  None')
    print()
    print('Missing required fields:')
    print('\n'.join(missing_records) if missing_records else '  None')
    print()
    print('Invalid note types:')
    print('\n'.join(invalid_types) if invalid_types else '  None')
    print()
    print('Invalid patient references:')
    print('\n'.join(invalid_patients) if invalid_patients else '  None')
    print()
    print('Invalid claim references:')
    print('\n'.join(invalid_claims) if invalid_claims else '  None')
    print()
    print('Invalid service dates:')
    print('\n'.join(invalid_dates) if invalid_dates else '  None')
    print()
    print('========================================================')


if __name__ == '__main__':
    validate_clinical_notes()
