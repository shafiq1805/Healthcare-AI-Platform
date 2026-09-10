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
    print("Error: 'clean_text' column missing.")
    sys.exit(1)


# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Create embeddings for clinical notes
note_embeddings = model.encode(
    df["clean_text"].tolist()
)


# Clinical query
query = "patient with diabetes and elevated blood glucose"


# Convert query into embedding
query_embedding = model.encode([query])


# Calculate similarity between query and every note
similarities = cosine_similarity(
    query_embedding,
    note_embeddings
)[0]


# Add similarity score to dataframe
df["similarity"] = similarities


# Sort highest similarity first
results = df.sort_values(
    by="similarity",
    ascending=False
)


print("========== CLINICAL SEMANTIC SEARCH ==========")
print()

print("Query:")
print(query)

print()

print("Top 5 relevant clinical notes:")
print()


for _, row in results.head(5).iterrows():

    print(
        f"{row['note_id']} | "
        f"Similarity: {row['similarity']:.4f}"
    )

    print(
        f"Patient: {row['patient_id']}"
    )

    print(
        f"Note: {row['clean_text']}"
    )

    print("----------------------------------------------")


print()
print("==============================================")
