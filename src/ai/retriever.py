import os
import sys
import pandas as pd

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class ClinicalRetriever:

    def __init__(
        self,
        input_path=r"data/processed/clinical_notes_processed.csv",
        model_name="all-MiniLM-L6-v2"
    ):

        if not os.path.exists(input_path):
            raise FileNotFoundError(
                f"Clinical notes file not found: {input_path}"
            )

        self.df = pd.read_csv(input_path)

        if "clean_text" not in self.df.columns:
            raise ValueError(
                "'clean_text' column missing from dataset."
            )

        if "note_id" not in self.df.columns:
            raise ValueError(
                "'note_id' column missing from dataset."
            )

        if "patient_id" not in self.df.columns:
            raise ValueError(
                "'patient_id' column missing from dataset."
            )

        print("Loading embedding model...")

        self.model = SentenceTransformer(model_name)

        print("Generating clinical note embeddings...")

        self.embeddings = self.model.encode(
            self.df["clean_text"].fillna("").tolist()
        )

        print(
            f"Loaded {len(self.df)} clinical notes."
        )

        print(
            f"Embedding dimensions: {self.embeddings.shape[1]}"
        )


    def search(
        self,
        query,
        top_k=5,
        threshold=0.40,
        patient_id=None
    ):

        if not query or not query.strip():
            raise ValueError(
                "Search query cannot be empty."
            )

        # --------------------------------------------------
        # Optional metadata filtering
        # --------------------------------------------------

        if patient_id:

            mask = (
                self.df["patient_id"].astype(str)
                == str(patient_id)
            )

            candidate_indices = self.df.index[mask].tolist()

        else:

            candidate_indices = self.df.index.tolist()


        if not candidate_indices:

            return []


        # --------------------------------------------------
        # Create query embedding
        # --------------------------------------------------

        query_embedding = self.model.encode(
            [query]
        )


        # --------------------------------------------------
        # Calculate similarity
        # --------------------------------------------------

        candidate_embeddings = self.embeddings[
            candidate_indices
        ]

        similarities = cosine_similarity(
            query_embedding,
            candidate_embeddings
        )[0]


        # --------------------------------------------------
        # Rank results
        # --------------------------------------------------

        ranked = sorted(
            zip(candidate_indices, similarities),
            key=lambda x: x[1],
            reverse=True
        )


        # --------------------------------------------------
        # Build structured results
        # --------------------------------------------------

        results = []

        for index, score in ranked:

            if score < threshold:
                continue

            row = self.df.loc[index]

            results.append(
                {
                    "note_id": row["note_id"],
                    "patient_id": row["patient_id"],
                    "encounter_id": row.get(
                        "encounter_id",
                        None
                    ),
                    "claim_id": row.get(
                        "claim_id",
                        None
                    ),
                    "note_type": row.get(
                        "note_type",
                        None
                    ),
                    "note_date": row.get(
                        "note_date",
                        None
                    ),
                    "similarity": round(
                        float(score),
                        4
                    ),
                    "text": row["clean_text"]
                }
            )


        # --------------------------------------------------
        # Return only Top-K
        # --------------------------------------------------

        return results[:top_k]


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print()
    print("========== CLINICAL RETRIEVER TEST ==========")
    print()

    try:

        retriever = ClinicalRetriever()

        query = (
            "patient with diabetes and "
            "elevated blood glucose"
        )

        results = retriever.search(
            query=query,
            top_k=5,
            threshold=0.40
        )

        print("Query:")
        print(query)
        print()

        print("Retrieved documents:")
        print()

        for result in results:

            print(
                f"{result['note_id']} | "
                f"Patient: {result['patient_id']} | "
                f"Similarity: {result['similarity']}"
            )

            print(
                f"Claim: {result['claim_id']}"
            )

            print(
                f"Text: {result['text']}"
            )

            print("------------------------------------------")


        print()
        print("============================================")


    except Exception as e:

        print(f"Error: {e}")
        sys.exit(1)
