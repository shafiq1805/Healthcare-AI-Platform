import pandas as pd
from sentence_transformers import SentenceTransformer

input_path = r"data/processed/clinical_notes_processed.csv"

df = pd.read_csv(input_path)

print("========== CLINICAL EMBEDDINGS ==========")
print()

# Load pretrained embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Generate embeddings
embeddings = model.encode(
    df["clean_text"].tolist(),
    show_progress_bar=True
)

print()
print("Number of notes:", len(embeddings))
print("Embedding dimensions:", embeddings.shape[1])
print("Embedding matrix shape:", embeddings.shape)

print()
print("First note:")
print(df.iloc[0]["note_id"])

print()
print("First 10 embedding values:")
print(embeddings[0][:10])

print()
print("==========================================")
