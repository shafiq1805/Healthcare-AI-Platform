import os
import sys
import oracledb
import pandas as pd

INSTANT_CLIENT_DIR = r"D:\abu\Study materials\Aimore\Data engineering\instantclient_23_26"

try:
    if os.path.exists(INSTANT_CLIENT_DIR):
        oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_DIR)
    else:
        oracledb.init_oracle_client()
except Exception as e:
    print(f"Notice during Oracle client initialization: {e}")


def load_clinical_notes_to_oracle():
    user = os.getenv('ORACLE_USER', 'HR')
    password = os.environ['ORACLE_PASSWORD']  # Required; never store credentials in source
    dsn = os.getenv('ORACLE_DSN', 'localhost:1521/XE')

    csv_path = r'data/processed/clinical_notes_processed.csv'

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    source_records = len(df)

    records = []
    for _, row in df.iterrows():
        # Ensure date string is cleanly formatted as YYYY-MM-DD
        formatted_date = pd.to_datetime(row['note_date']).strftime('%Y-%m-%d')

        records.append((
            str(row['note_id']),
            str(row['patient_id']),
            str(row['encounter_id']),
            str(row['claim_id']),
            str(row['note_type']),
            formatted_date,
            str(row['author_provider_id']),
            str(row['note_text'])
        ))

    # Explicitly map YYYY-MM-DD using TO_DATE with exact mask
    sql_insert = """
        INSERT INTO clinical_notes (
            note_id,
            patient_id,
            encounter_id,
            claim_id,
            note_type,
            note_date,
            author_provider_id,
            note_text
        ) VALUES (
            :1, :2, :3, :4, :5, TO_DATE(:6, 'YYYY-MM-DD'), :7, :8
        )
    """

    inserted_count = 0

    try:
        with oracledb.connect(
            user=user, password=password, dsn=dsn
        ) as connection:
            with connection.cursor() as cursor:
                cursor.executemany(sql_insert, records)
                inserted_count = cursor.rowcount
                connection.commit()

        print("========== CLINICAL NOTES LOAD ==========")
        print(f"Source records: {source_records}")
        print(f"Records inserted: {inserted_count}")
        print("Target table: CLINICAL_NOTES")
        print("Load status: SUCCESS")
        print("==========================================")

    except oracledb.Error as e:
        print("========== CLINICAL NOTES LOAD ==========")
        print(f"Source records: {source_records}")
        print("Records inserted: 0")
        print("Target table: CLINICAL_NOTES")
        print("Load status: FAILED")
        print(f"Error Details: {e}")
        print("==========================================")


if __name__ == '__main__':
    load_clinical_notes_to_oracle()
