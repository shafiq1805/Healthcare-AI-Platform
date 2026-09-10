# Local data

Healthcare records are excluded from Git. Keep raw, processed, and quarantine
datasets on your local machine. Do not commit patient information or claims records.

The API expects these files relative to the repository root:

- `data/processed/patients_processed.csv`
- `data/processed/claims_processed.csv`
- `data/processed/clinical_notes_processed.csv`

ETL scripts also use `data/raw/` and write to `data/processed/` and
`data/quarantine/`. Create these directories when setting up a fresh clone.
Consult the processing scripts and `sql/schema.sql` for field requirements.
Supply your own synthetic demonstration data; no dataset is bundled.
