import ollama
from retriever import ClinicalRetriever
from context_builder import build_context


def build_rag_prompt(query, context):

    prompt = f"""
You are a healthcare data assistant.

FINAL INSTRUCTION:

Answer ONLY from the clinical context.

Return exactly this format:

Patient ID: <patient_id>
Note ID: <note_id>
Evidence: <exact sentence from the clinical documentation>

For the current question, the correct evidence must explicitly
show elevated blood glucose.

Do NOT use diabetes alone as evidence.

Do NOT use Claim ID as Note ID.

Do NOT add information that is not present in the clinical context.

If no document explicitly supports the answer, return:

Patient ID: NOT FOUND
Note ID: NOT FOUND
Evidence: The available clinical documentation does not contain enough information.

USER QUESTION:
{query}

CLINICAL CONTEXT:
{context}

ANSWER:
"""

    return prompt.strip()


if __name__ == "__main__":

    print("========== RAG PIPELINE TEST ==========")
    print()

    retriever = ClinicalRetriever()

    query = "Which patient has documented cough?"

    # Retrieve relevant notes
    results = retriever.search(
        query=query,
        top_k=3,
        threshold=0.40
    )

    # Build context
    context = build_context(results)

    # Build LLM prompt
    prompt = build_rag_prompt(
        query=query,
        context=context
    )

    print("USER QUESTION:")
    print(query)

    print()
    print("RETRIEVED DOCUMENTS:")
    print(len(results))

    print()
    print("========== GENERATED RAG PROMPT ==========")
    response = ollama.chat(
        model="qwen2.5:0.5b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response["message"]["content"]

    print("========== GENERATED ANSWER ==========")
    print()
    print(answer)
    print()
    print("=======================================")
    print()
    print(prompt)

    print()
    print("==========================================")
