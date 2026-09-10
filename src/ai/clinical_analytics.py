import os
import sys
import pandas as pd


def generate_clinical_analytics():
    patients_path = r'data/processed/patients_processed.csv'
    claims_path = r'data/processed/claims_processed.csv'
    notes_path = r'data/processed/clinical_notes_processed.csv'

    # Path variants for claim-diagnosis mappings
    claims_diag_paths = [
        r'data/processed/claims_diagnoses_processed.csv',
        r'data/processed/diagnoses_processed.csv',
        r'data/processed/claim_diagnoses_processed.csv'
    ]

    # Check required core processed CSV paths
    for path in [patients_path, claims_path, notes_path]:
        if not os.path.exists(path):
            print(f"Error: Required file not found at {path}")
            sys.exit(1)

    df_patients = pd.read_csv(patients_path)
    df_claims = pd.read_csv(claims_path)
    df_notes = pd.read_csv(notes_path)

    total_patients = df_patients['patient_id'].nunique()
    total_claims = df_claims['claim_id'].nunique()
    total_clinical_notes = len(df_notes)

    # Check for procedures dataset
    procedures_path = r'data/processed/procedures_processed.csv'
    if os.path.exists(procedures_path):
        df_procedures = pd.read_csv(procedures_path)
        total_procedures = len(df_procedures)
    else:
        total_procedures = total_claims

    # Load Diagnoses from relational mapping table
    df_diagnoses = None
    for p in claims_diag_paths:
        if os.path.exists(p):
            df_diagnoses = pd.read_csv(p)
            break

    if df_diagnoses is not None and 'diagnosis_code' in df_diagnoses.columns:
        total_diagnoses = len(df_diagnoses)
        top_diagnoses = (
            df_diagnoses['diagnosis_code']
            .value_counts()
            .head(5)
            .to_dict()
        )
    else:
        total_diagnoses = 0
        top_diagnoses = {}

    # Claim Status Aggregations
    status_counts = (
        df_claims['claim_status'].astype(str).str.upper().value_counts()
    )
    paid_count = status_counts.get('PAID', 0)
    denied_count = status_counts.get('DENIED', 0)
    pending_count = status_counts.get('PENDING', 0)
    submitted_count = status_counts.get('SUBMITTED', 0)

    # Financial Aggregations
    total_charges = df_claims['total_charge'].astype(float).sum()

    # Print Analytics Output
    print("========== CLINICAL ANALYTICS ==========")
    print()
    print(f"Total patients:       {total_patients}")
    print(f"Total claims:         {total_claims}")
    print(f"Total procedures:     {total_procedures}")
    print(f"Total diagnoses:      {total_diagnoses}")
    print(f"Total clinical notes: {total_clinical_notes}")
    print()
    print("---------- CLAIM STATUS ----------")
    print(f"PAID:      {paid_count}")
    print(f"DENIED:    {denied_count}")
    print(f"PENDING:   {pending_count}")
    print(f"SUBMITTED: {submitted_count}")
    print()
    print("---------- FINANCIAL ----------")
    print(f"Total charges: ${total_charges:,.2f}")
    print()
    print("---------- TOP DIAGNOSES ----------")
    if top_diagnoses:
        for code, count in top_diagnoses.items():
            print(f"{code:<7} → {count}")
    else:
        print("No diagnosis records found.")
    print()
    print("========================================")


if __name__ == '__main__':
    generate_clinical_analytics()
