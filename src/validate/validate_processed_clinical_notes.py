import os
import sys
import pandas as pd


def validate_processed_clinical_notes():
    processed_notes_path = r'data/processed/clinical_notes_processed.csv'
    processed_patients_path = r'data/processed/patients_processed.csv'
    processed_claims_path = r'data/processed/claims_processed.csv'

    for path in [processed_notes_path, processed_patients_path, processed_claims_path]:
        if not os.path.exists(path):
            print(f"Error: File not found at {path}")
            sys.exit(1)

    df_notes = pd.read_csv(processed_notes_path)
    df_patients = pd.read_csv(processed_patients_path)
    df_claims = pd.read_csv(processed_claims_path)

    total_notes = len(df_notes)

    # 1. Duplicate note IDs
    duplicate_note_ids = df_notes.duplicated(subset=['note_id']).sum()

    # 2. Patient referential integrity
    valid_patient_ids = set(df_patients['patient_id'].dropna().unique())
    invalid_patient_refs = (~df_notes['patient_id'].isin(valid_patient_ids)).sum()

    # 3. Claim referential integrity
    valid_claim_ids = set(df_claims['claim_id'].dropna().unique())
    invalid_claim_refs = (~df_notes['claim_id'].isin(valid_claim_ids)).sum()

    # 4. Missing required fields
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
    missing_fields_count = df_notes[required_cols].isna().any(axis=1).sum()

    # 5. Invalid note types
    allowed_types = ['SOAP', 'PROGRESS', 'DISCHARGE', 'OPERATIVE']
    invalid_note_types = (~df_notes['note_type'].isin(allowed_types)).sum()

    # 6. Invalid dates
    parsed_dates = pd.to_datetime(df_notes['note_date'], errors='coerce')
    invalid_dates_count = parsed_dates.isna().sum()

    # 7. Empty clinical text (Checks for NaN or whitespace-only strings)
    empty_notes_count = (
        df_notes['note_text'].isna() | (df_notes['note_text'].astype(str).str.strip() == '')
    ).sum()

    # Determine overall validation status
    all_passed = all([
        duplicate_note_ids == 0,
        invalid_patient_refs == 0,
        invalid_claim_refs == 0,
        missing_fields_count == 0,
        invalid_note_types == 0,
        invalid_dates_count == 0,
        empty_notes_count == 0,
    ])

    status = "PASS" if all_passed else "FAIL"

    # Print Quality Audit Report
    print("========== PROCESSED CLINICAL NOTES VALIDATION ==========")
    print()
    print(f"Total notes: {total_notes}")
    print()
    print(f"Duplicate note IDs: {duplicate_note_ids}")
    print(f"Invalid patient references: {invalid_patient_refs}")
    print(f"Invalid claim references: {invalid_claim_refs}")
    print(f"Missing required fields: {missing_fields_count}")
    print(f"Invalid note types: {invalid_note_types}")
    print(f"Invalid service dates: {invalid_dates_count}")
    print(f"Empty clinical notes: {empty_notes_count}")
    print()
    print("==========================================================")
    print(f"STATUS: {status}")


if __name__ == '__main__':
    validate_processed_clinical_notes()
