CREATE TABLE patients (
    patient_id        VARCHAR2(50)  NOT NULL,
    first_name        VARCHAR2(100) NOT NULL,
    last_name         VARCHAR2(100) NOT NULL,
    date_of_birth     DATE          NOT NULL,
    gender            VARCHAR2(20)  DEFAULT 'Unknown' NOT NULL,
    email             VARCHAR2(255),
    phone             VARCHAR2(50),
    insurance_id      VARCHAR2(100),
    created_at        TIMESTAMP     DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at        TIMESTAMP     DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT pk_patients PRIMARY KEY (patient_id),
    CONSTRAINT chk_patients_gender CHECK (gender IN ('M', 'F', 'Unknown'))
);

-- -----------------------------------------------------------------------------
-- Step 2: Claims Table (Header level entity, depends on patients)
-- -----------------------------------------------------------------------------
CREATE TABLE claims (
    claim_id          VARCHAR2(50)  NOT NULL,
    patient_id        VARCHAR2(50)  NOT NULL,
    service_date      DATE          NOT NULL,
    provider_id       VARCHAR2(50)  NOT NULL,
    payer             VARCHAR2(100) NOT NULL,
    claim_status      VARCHAR2(20)  NOT NULL,
    total_charge      NUMBER(10, 2) NOT NULL,
    created_at        TIMESTAMP     DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT pk_claims PRIMARY KEY (claim_id),
    CONSTRAINT fk_claims_patients FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id),
    CONSTRAINT chk_claim_status CHECK (claim_status IN ('SUBMITTED', 'PAID', 'DENIED', 'PENDING'))
);

-- -----------------------------------------------------------------------------
-- Step 3a: Claim Diagnoses Table (Line items, depends on claims)
-- -----------------------------------------------------------------------------
CREATE TABLE claim_diagnoses (
    claim_diagnosis_id NUMBER(19)    GENERATED ALWAYS AS IDENTITY,
    claim_id           VARCHAR2(50)  NOT NULL,
    diagnosis_code     VARCHAR2(20)  NOT NULL,
    diagnosis_type     VARCHAR2(20)  DEFAULT 'SECONDARY' NOT NULL,
    sequence_num       NUMBER(3)     NOT NULL,

    CONSTRAINT pk_claim_diagnoses PRIMARY KEY (claim_diagnosis_id),
    CONSTRAINT fk_diagnoses_claims FOREIGN KEY (claim_id)
        REFERENCES claims(claim_id),
    CONSTRAINT chk_diag_type CHECK (diagnosis_type IN ('PRIMARY', 'SECONDARY', 'ADMITTING'))
);

-- -----------------------------------------------------------------------------
-- Step 3b: Claim Procedures Table (Line items, depends on claims)
-- -----------------------------------------------------------------------------
CREATE TABLE claim_procedures (
    claim_procedure_id NUMBER(19)    GENERATED ALWAYS AS IDENTITY,
    claim_id           VARCHAR2(50)  NOT NULL,
    procedure_code     VARCHAR2(20)  NOT NULL,
    procedure_type     VARCHAR2(20)  DEFAULT 'CPT' NOT NULL,
    service_date       DATE          NOT NULL,
    units              NUMBER(5)     DEFAULT 1 NOT NULL,
    line_charge        NUMBER(10, 2) NOT NULL,

    CONSTRAINT pk_claim_procedures PRIMARY KEY (claim_procedure_id),
    CONSTRAINT fk_procedures_claims FOREIGN KEY (claim_id)
        REFERENCES claims(claim_id)
);

-- -----------------------------------------------------------------------------
-- Step 4: Clinical Notes Table (Unstructured clinical text for GenAI)
-- -----------------------------------------------------------------------------
CREATE TABLE clinical_notes (
    note_id           VARCHAR2(50)  NOT NULL,
    patient_id        VARCHAR2(50)  NOT NULL,
    encounter_id      VARCHAR2(50),
    claim_id          VARCHAR2(50),
    note_type         VARCHAR2(50)  NOT NULL,
    note_date         DATE          NOT NULL,
    author_provider_id VARCHAR2(50),
    note_text         CLOB          NOT NULL,
    created_at        TIMESTAMP     DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT pk_clinical_notes PRIMARY KEY (note_id),
    CONSTRAINT fk_notes_patients FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id),
    CONSTRAINT fk_notes_claims FOREIGN KEY (claim_id)
        REFERENCES claims(claim_id) ON DELETE SET NULL
);
