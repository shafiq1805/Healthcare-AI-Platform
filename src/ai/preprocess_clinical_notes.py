import os
import re
import sys
import pandas as pd


def preprocess_text(text: str) -> str:
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def run_text_preprocessing():
    csv_path = r"data/processed/clinical_notes_processed.csv"

    if not os.path.exists(csv_path):
        print(f"Error: Processed CSV not found at {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)

    # Apply conservative preprocessing
    df["clean_text"] = df["note_text"].apply(preprocess_text)

    # EXPLICITLY OVERWRITE CSV TO SAVE 'clean_text' PERMANENTLY
    df.to_csv(csv_path, index=False)

    print("========== CLINICAL TEXT PREPROCESSING ==========")
    print()
    print("Successfully updated CSV with 'clean_text' column.")
    print()

    for _, row in df.head(3).iterrows():
        print(f"{row['note_id']}")
        print()
        print("Original:")
        print(f"{row['note_text']}")
        print()
        print("Processed:")
        print(f"{row['clean_text']}")
        print()

    print("=================================================")


if __name__ == "__main__":
    run_text_preprocessing()
