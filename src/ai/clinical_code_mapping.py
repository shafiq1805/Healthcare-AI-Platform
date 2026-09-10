import os
import re
import sys
import pandas as pd

CODE_MAP = {
    "upper respiratory": "J06.9",
    "type 2 diabetes": "E11.9",
    "hyperlipidemia": "E78.5",
    "low back pain": "M54.5",
    "hypertension": "I10",
    "sore throat": "J02.9",
    "diabetes": "E11.9",
    "cough": "R05.9",
    "gerd": "K21.9",
}


def preprocess_text(text: str) -> str:
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_icd10_codes(text: str) -> dict:
    matched_codes = {}
    # Iterate over terms sorted by length in descending order to avoid duplicate sub-phrase matches
    sorted_terms = sorted(CODE_MAP.keys(), key=len, reverse=True)

    for term in sorted_terms:
        code = CODE_MAP[term]
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, text):
            # Map canonical condition term if a generic sub-term like 'diabetes' overlaps 'type 2 diabetes'
            if code not in matched_codes.values():
                matched_codes[term] = code

    return matched_codes


def run_clinical_code_mapping():
    csv_path = r"data/processed/clinical_notes_processed.csv"

    if not os.path.exists(csv_path):
        print(f"Error: Processed CSV not found at {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)

    if "clean_text" not in df.columns:
        df["clean_text"] = df["note_text"].apply(preprocess_text)

    print("========== CLINICAL CODE MAPPING ==========")
    print()

    for _, row in df.iterrows():
        note_id = row["note_id"]
        patient_id = row["patient_id"]
        text = str(row["clean_text"])

        mapped_codes = extract_icd10_codes(text)

        if mapped_codes:
            print(f"{note_id} | {patient_id}")
            for term, code in mapped_codes.items():
                print(f"{term:<14} → {code}")
            print()

    print("============================================")


if __name__ == "__main__":
    run_clinical_code_mapping()
