import os
import sys
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

input_path = r"data/processed/clinical_notes_processed.csv"

if not os.path.exists(input_path):
    print(f"Error: File not found at {input_path}")
    sys.exit(1)

df = pd.read_csv(input_path)

if "clean_text" not in df.columns:
    print("Error: 'clean_text' column missing. Run preprocess_clinical_notes.py first.")
    sys.exit(1)

model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(df["clean_text"].tolist())

# Calculate similarity between every pair of notes
similarity_matrix = cosine_similarity(embeddings)

# Helper function to dynamically get the matrix index for a given note_id
def get_note_index(note_id: str) -> int:
    indices = df.index[df["note_id"] == note_id].tolist()
    if not indices:
        raise ValueError(f"Note ID {note_id} not found in processed dataset.")
    return indices[0]

idx_cn5001 = get_note_index("CN5001")
idx_cn5002 = get_note_index("CN5002")
idx_cn5007 = get_note_index("CN5007")
idx_cn5018 = get_note_index("CN5018")

print("========== CLINICAL NOTE SIMILARITY ==========")
print()
print("Number of notes:", len(df))
print("Similarity matrix shape:", similarity_matrix.shape)
print()
print("Similarity between CN5001 and CN5002 (Diabetes/HTN vs Respiratory):")
print(round(similarity_matrix[idx_cn5001][idx_cn5002], 4))
print()
print("Similarity between CN5001 and CN5007 (Diabetes/HTN vs Chronic HTN):")
print(round(similarity_matrix[idx_cn5001][idx_cn5007], 4))
print()
print("Similarity between CN5001 and CN5018 (Diabetes/HTN vs Uncontrolled Diabetes):")
print(round(similarity_matrix[idx_cn5001][idx_cn5018], 4))
print()
print("==============================================")
