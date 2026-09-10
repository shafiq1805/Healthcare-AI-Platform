import os
import sys
import oracledb
import pandas as pd

# Path to your extracted Oracle Instant Client
INSTANT_CLIENT_DIR = r"D:\abu\Study materials\Aimore\Data engineering\instantclient_23_26"

# Initialize Thick Mode for backward compatibility
try:
    if os.path.exists(INSTANT_CLIENT_DIR):
        oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_DIR)
    else:
        oracledb.init_oracle_client()
except Exception as e:
    print(f"Notice during Oracle client initialization: {e}")


def load_diagnoses_to_oracle():
    # Database Connection Parameters
    user = os.getenv('ORACLE_USER', 'HR')
    password = os.environ['ORACLE_PASSWORD']  # Required; never store credentials in source
    dsn = os.getenv('ORACLE_DSN', 'localhost:1521/XE')

    csv_path = r'D:\App development\Healthcare AI Platform\data\processed\claim_diagnoses_processed.csv'

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    source_records = len(df)

    # Pass claim_diagnosis_id directly from the CSV
    records = []
    for _, row in df.iterrows():
        records.append((
            row['claim_diagnosis_id'],
            row['claim_id'],
            row['diagnosis_code'],
            row['diagnosis_type'],
            int(row['sequence_num']),
        ))

    sql_insert = """
        INSERT INTO claim_diagnoses (
            claim_diagnosis_id,
            claim_id,
            diagnosis_code,
            diagnosis_type,
            sequence_num
        ) VALUES (
            :1, :2, :3, :4, :5
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

        print("========== DIAGNOSIS LOAD ==========")
        print(f"Source records: {source_records}")
        print(f"Records inserted: {inserted_count}")
        print("Target table: CLAIM_DIAGNOSES")
        print("Load status: SUCCESS")
        print("====================================")

    except oracledb.Error as e:
        print("========== DIAGNOSIS LOAD ==========")
        print(f"Source records: {source_records}")
        print("Records inserted: 0")
        print("Target table: CLAIM_DIAGNOSES")
        print("Load status: FAILED")
        print(f"Error Details: {e}")
        print("====================================")


if __name__ == '__main__':
    load_diagnoses_to_oracle()
