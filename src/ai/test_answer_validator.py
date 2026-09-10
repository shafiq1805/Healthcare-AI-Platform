# Synthetic fixture for demonstrating evidence validation.
from answer_validator import validate_answer


context = """
DOCUMENT 1

Patient ID: SYNTHETIC-PATIENT-001
Note ID: SYNTHETIC-NOTE-001

Clinical Documentation:
follow up for uncontrolled type 2 diabetes mellitus
fasting blood glucose elevated
medication dose adjusted
"""


answer = {
    "patient_id": "SYNTHETIC-PATIENT-001",
    "note_id": "SYNTHETIC-NOTE-001",
    "evidence": "patient is taking metformin"
}


result = validate_answer(answer, context)

print(result)
