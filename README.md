# Healthcare AI Platform

An end-to-end healthcare data engineering and GenAI platform built using
Python, Oracle, FastAPI, Streamlit, NLP, embeddings, RAG, and Ollama.

## Architecture

EHR / Claims / Clinical Notes
        ↓
Data Quality & ETL
        ↓
Processed Healthcare Data
        ↓
Oracle Healthcare Database
        ↓
Clinical NLP
        ↓
Embeddings & Semantic Search
        ↓
RAG
        ↓
Local LLM (Ollama)
        ↓
FastAPI
        ↓
Streamlit Healthcare UI

## Technology Stack

- Python
- Pandas
- SQL / Oracle
- FastAPI
- Streamlit
- Sentence Transformers
- Scikit-learn
- RAG
- Ollama
- Qwen
- REST APIs

## Healthcare Data

The platform processes:

- Patients
- Claims
- Claim diagnoses
- Claim procedures
- Clinical notes

Data quality checks include:

- Duplicate detection
- Missing values
- Invalid dates
- Invalid references
- Invalid codes
- Invalid status values
- Referential integrity

Invalid records are quarantined rather than silently loaded.

## AI Capabilities

### Clinical NLP

- Text cleaning
- Tokenization
- TF-IDF
- Sentence embeddings
- Semantic similarity

### Clinical Search

Search clinical documentation using semantic similarity.

### RAG

Retrieve relevant clinical documentation and provide grounded answers.

### Clinical Entity Extraction

Extract:

- Diagnoses
- Symptoms
- Findings
- Clinical actions

### Clinical Code Mapping

Map selected clinical concepts to controlled ICD-10-style codes.

## API

FastAPI provides:

- `GET /health`
- `GET /patients/{patient_id}`
- `GET /claims`
- `GET /analytics`
- `POST /search`
- `POST /ask`

## User Interface

Streamlit provides:

- Healthcare dashboard
- Claim analytics
- Clinical search
- Patient explorer
- Clinical AI assistant

## Local setup

This repository contains the source code and SQL schema. Healthcare datasets,
spreadsheets, virtual environments, and local credentials are intentionally excluded.
Use synthetic data for demonstrations. Data-dependent features need local CSV files;
see [data/README.md](data/README.md).

```bash
git clone https://github.com/shafiq1805/Healthcare-AI-Platform.git
cd Healthcare-AI-Platform
python -m venv .venv
```

Activate the environment (`.venv\Scripts\Activate.ps1` on Windows PowerShell,
or `source .venv/bin/activate` on macOS/Linux), then install dependencies:

```bash
python -m pip install -r requirements.txt
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

In a second terminal with the environment activated:

```bash
python -m streamlit run app.py
```

The API health endpoint is `http://127.0.0.1:8000/health` and its documentation
is at `http://127.0.0.1:8000/docs`.

### Configuration and current limitations

- Oracle loaders require `ORACLE_PASSWORD` in the shell environment. See
  `.env.example` for the variable names; the application does not load that file automatically.
- Some ETL scripts contain paths for the original Windows development machine.
  Update those paths and Oracle Instant Client locations before running them elsewhere.
- Ollama-based scripts require a locally running Ollama service and the model
  specified by the script. Embedding scripts may download model weights on first use.
- Dependencies are listed in `requirements.txt`; a fully pinned, reproducible lockfile
  is not yet provided.
- This is a development portfolio project. Clinical accuracy and production readiness
  have not been independently validated.

### Evidence validation example

Run the synthetic example without healthcare datasets:

```bash
python src/ai/test_answer_validator.py
```

The example intentionally supplies unsupported evidence. The expected result is
`FAIL` with `Evidence not found in retrieved context`.
