import os
import pandas as pd


def process_clinical_notes():
    raw_notes_path = r'data/raw/clinical_notes.csv'
    processed_patients_path = r'data/processed/patients_processed.csv'
    processed_claims_path = r'data/processed/claims_processed.csv'

    output_processed_path = r'data/processed/clinical_notes_processed.csv'
    output_quarantine_path = r'data/quarantine/clinical_notes_quarantine.csv'

    # Ensure output directories exist
    os.makedirs(os.path.dirname(output_processed_path), exist_ok=True)
    os.makedirs(os.path.dirname(output_quarantine_path), exist_ok=True)

    # 1. Load Data
    df_raw = pd.read_csv(raw_notes_path).dropna(how='all')
    df_patients = pd.read_csv(processed_patients_path)
    df_claims = pd.read_csv(processed_claims_path)

    raw_count = len(df_raw)
    valid_patient_ids = set(df_patients['patient_id'].dropna().unique())
    valid_claim_ids = set(df_claims['claim_id'].dropna().unique())
    allowed_types = ['SOAP', 'PROGRESS', 'DISCHARGE', 'OPERATIVE']

    processed_rows = []
    quarantine_rows = []

    # Rule Violation Counter (Tracks total rule failures across all records)
    rule_violation_counts = {
        'DUPLICATE_NOTE_ID': 0,
        'INVALID_PATIENT_REFERENCE': 0,
        'INVALID_CLAIM_REFERENCE': 0,
        'MISSING_NOTE_TEXT': 0,
        'INVALID_NOTE_TYPE': 0,
    }

    seen_note_ids = set()

    # 2. Process Records
    for _, row in df_raw.iterrows():
        note_dict = row.to_dict()
        record_reasons = []

        # Rule 1: Duplicate Note ID
        note_id = note_dict.get('note_id')
        if note_id in seen_note_ids:
            record_reasons.append('DUPLICATE_NOTE_ID')
            rule_violation_counts['DUPLICATE_NOTE_ID'] += 1
        else:
            if pd.notna(note_id):
                seen_note_ids.add(note_id)

        # Rule 2: Invalid Patient Reference
        patient_id = note_dict.get('patient_id')
        if pd.isna(patient_id) or patient_id not in valid_patient_ids:
            record_reasons.append('INVALID_PATIENT_REFERENCE')
            rule_violation_counts['INVALID_PATIENT_REFERENCE'] += 1

        # Rule 3: Invalid Claim Reference
        claim_id = note_dict.get('claim_id')
        if pd.isna(claim_id) or claim_id not in valid_claim_ids:
            record_reasons.append('INVALID_CLAIM_REFERENCE')
            rule_violation_counts['INVALID_CLAIM_REFERENCE'] += 1

        # Rule 4: Missing Note Text
        note_text = note_dict.get('note_text')
        if pd.isna(note_text) or str(note_text).strip() == '':
            record_reasons.append('MISSING_NOTE_TEXT')
            rule_violation_counts['MISSING_NOTE_TEXT'] += 1

        # Rule 5: Invalid Note Type
        note_type = note_dict.get('note_type')
        if pd.isna(note_type) or note_type not in allowed_types:
            record_reasons.append('INVALID_NOTE_TYPE')
            rule_violation_counts['INVALID_NOTE_TYPE'] += 1

        # Routing Decision
        if record_reasons:
            note_dict['quarantine_reason'] = ';'.join(record_reasons)
            quarantine_rows.append(note_dict)
        else:
            processed_rows.append(note_dict)

    # 3. Create DataFrames & Export CSVs
    df_processed = pd.DataFrame(processed_rows)
    df_quarantine = pd.DataFrame(quarantine_rows)

    df_processed.to_csv(output_processed_path, index=False)
    df_quarantine.to_csv(output_quarantine_path, index=False)

    duplicate_records_count = rule_violation_counts['DUPLICATE_NOTE_ID']
    unique_records_count = raw_count - duplicate_records_count

    # 4. Audit Summary Printout
    print('========== CLINICAL NOTES TRANSFORMATION ==========')
    print()
    print(f'Raw records:              {raw_count}')
    print(f'Duplicate records:         {duplicate_records_count}')
    print(f'Unique records:           {unique_records_count}')
    print()
    print(f'Quarantined notes:        {len(df_quarantine)}')
    print(f'Processed notes:          {len(df_processed)}')
    print()
    print('Quarantine rule violations:')
    print(f"Duplicate note ID:                 {rule_violation_counts['DUPLICATE_NOTE_ID']}")
    print(f"Invalid patient reference:         {rule_violation_counts['INVALID_PATIENT_REFERENCE']}")
    print(f"Invalid claim reference:           {rule_violation_counts['INVALID_CLAIM_REFERENCE']}")
    print(f"Missing note text:                 {rule_violation_counts['MISSING_NOTE_TEXT']}")
    print(f"Invalid note type:                 {rule_violation_counts['INVALID_NOTE_TYPE']}")
    print()
    print('====================================================')


if __name__ == '__main__':
    process_clinical_notes()
