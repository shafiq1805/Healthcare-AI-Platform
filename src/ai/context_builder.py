from retriever import ClinicalRetriever


def build_context(results):
    """
    Convert retrieved clinical notes into
    structured context for an LLM.
    """

    if not results:
        return "No relevant clinical notes were found."

    context_parts = []

    for i, result in enumerate(results, start=1):

        context = f"""
DOCUMENT {i}

Patient ID: {result['patient_id']}
Note ID: {result['note_id']}
Claim ID: {result['claim_id']}
Encounter ID: {result['encounter_id']}
Note Type: {result['note_type']}
Note Date: {result['note_date']}
Similarity Score: {result['similarity']}

Clinical Documentation:
{result['text']}
"""

        context_parts.append(context.strip())

    return "\n\n".join(context_parts)


if __name__ == "__main__":

    print("========== CONTEXT BUILDER TEST ==========")
    print()

    retriever = ClinicalRetriever()

    query = "patient with diabetes and elevated blood glucose"

    results = retriever.search(
        query=query,
        top_k=3,
        threshold=0.40
    )

    context = build_context(results)

    print("Query:")
    print(query)

    print()
    print("Generated Context:")
    print()
    print(context)

    print()
    print("==========================================")
