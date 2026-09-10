import os
import sys
import pandas as pd


def tokenize_clinical_notes():
    csv_path = r"data/processed/clinical_notes_processed.csv"

    if not os.path.exists(csv_path):
        print(f"Error: Processed CSV not found at {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)

    if "clean_text" not in df.columns:
        print("Error: 'clean_text' column missing. Run preprocess_clinical_notes.py first.")
        sys.exit(1)

    # Tokenization on pre-saved clean_text column
    df["tokens"] = df["clean_text"].fillna("").apply(lambda x: x.split())
    df["token_count"] = df["tokens"].apply(len)

    total_tokens = df["token_count"].sum()
    avg_tokens = df["token_count"].mean()

    print("========== CLINICAL TEXT TOKENIZATION ==========")
    print()
    print(f"Total tokens across all notes: {total_tokens}")
    print(f"Average tokens per note:       {avg_tokens:.1f}")
    print()
    print("---------- SAMPLE TOKENIZED NOTES ----------")
    print()

    for _, row in df.head(3).iterrows():
        print(f"{row['note_id']}")
        print(f"Clean Text:  {row['clean_text']}")
        print(f"Token Count: {row['token_count']}")
        print("Tokens:")
        print(row["tokens"])
        print()

    print("================================================")


if __name__ == "__main__":
    tokenize_clinical_notes()
