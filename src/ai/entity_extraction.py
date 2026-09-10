import os
import re
import sys
import pandas as pd

DIAGNOSIS_TERMS = [
    "diabetes",
    "hypertension",
    "hyperlipidemia",
    "gerd",
]

SYMPTOM_TERMS = [
    "cough",
    "fatigue",
    "sore throat",
    "heartburn",
    "shortness of breath",
    "dizziness",
]

FINDING_TERMS = [
    "blood glucose elevated",
    "bp",
    "chest clear",
    "lungs clear",
]

ACTION_TERMS = [
    "medication dose adjusted",
    "prescribed",
    "ordered",
    "performed",
    "started",
    "switched",
]

CATEGORIES = {
    "DIAGNOSIS": DIAGNOSIS_TERMS,
    "SYMPTOMS": SYMPTOM_TERMS,
    "FINDINGS": FINDING_TERMS,
    "ACTIONS": ACTION_TERMS,
}


def preprocess_text(text: str) -> str:
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_entities(text: str, terms: list) -> list:
    extracted = []
    for term in terms:
        # Use regex word boundaries (\b) to match whole words/phrases accurately
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, text):
            extracted.append(term)
    return extracted


def run_entity_extraction():
    csv_path = r"data/processed/clinical_notes_processed.csv"

    if not os.path.exists(csv_path):
        print(f"Error: Processed CSV not found at {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)

    # Ensure clean_text column exists
    if "clean_text" not in df.columns:
        df["clean_text"] = df["note_text"].apply(preprocess_text)

    print("========== CLINICAL ENTITY EXTRACTION ==========")
    print()

    for _, row in df.iterrows():
        note_id = row["note_id"]
        patient_id = row["patient_id"]
        text = str(row["clean_text"])

        print(f"{note_id}")
        print(f"Patient: {patient_id}")
        print()

        for category, terms in CATEGORIES.items():
            matches = extract_entities(text, terms)
            print(f"{category}:")
            if matches:
                for match in matches:
                    print(f"- {match}")
            else:
                print("None")

        print("-" * 42)
        print()

    print("================================================")


if __name__ == "__main__":
    run_entity_extraction()
