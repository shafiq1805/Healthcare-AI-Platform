import os
import sys
import pandas as pd


def inspect_clinical_notes():
    csv_path = r'data/processed/clinical_notes_processed.csv'

    if not os.path.exists(csv_path):
        print(f"Error: Processed clinical notes CSV not found at {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)

    total_notes = len(df)
    unique_patients = df['patient_id'].nunique()
    unique_claims = df['claim_id'].nunique()

    # Calculate note length metrics
    df['note_length'] = df['note_text'].astype(str).str.len()

    avg_length = df['note_length'].mean()
    min_length = df['note_length'].min()
    max_length = df['note_length'].max()

    print("========== CLINICAL TEXT INSPECTION ==========")
    print()
    print(f"Total notes: {total_notes}")
    print(f"Unique patients: {unique_patients}")
    print(f"Unique claims: {unique_claims}")
    print()
    print(f"Average note length: {avg_length:.1f} characters")
    print(f"Minimum note length: {min_length} characters")
    print(f"Maximum note length: {max_length} characters")
    print()
    print("---------- NOTE LENGTHS ----------")
    print()
    for _, row in df[['note_id', 'note_type', 'note_length']].iterrows():
        print(f"{row['note_id']} | {row['note_type']:<8} | {row['note_length']} chars")
    print()
    print("---------- SAMPLE NOTES ----------")
    print()
    for _, row in df.head(3).iterrows():
        print(f"{row['note_id']}:")
        print(f"{row['note_text']}")
        print()
    print("==============================================")


if __name__ == '__main__':
    inspect_clinical_notes()
