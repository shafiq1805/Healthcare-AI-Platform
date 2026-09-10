def validate_answer(answer: dict, context: str) -> dict:
    """
    Validate whether an AI-generated clinical answer
    is grounded in the retrieved clinical context.
    """

    patient_id = answer.get("patient_id")
    note_id = answer.get("note_id")
    evidence = answer.get("evidence")

    # Required fields
    if not patient_id or not note_id or not evidence:
        return {
            "status": "FAIL",
            "reason": "Missing required answer fields",
            "answer": None
        }

    # Patient must exist in retrieved context
    if patient_id not in context:
        return {
            "status": "FAIL",
            "reason": "Patient ID not found in retrieved context",
            "answer": None
        }

    # Note must exist in retrieved context
    if note_id not in context:
        return {
            "status": "FAIL",
            "reason": "Note ID not found in retrieved context",
            "answer": None
        }

    # Evidence must appear in retrieved context
    evidence_text = evidence.lower().strip()

    if evidence_text not in context.lower():
        return {
            "status": "FAIL",
            "reason": "Evidence not found in retrieved context",
            "answer": None
        }

    # Everything passed
    return {
        "status": "PASS",
        "reason": "Answer is grounded in retrieved context",
        "answer": answer
    }
