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


def load_procedures_to_oracle():
    user = os.getenv('ORACLE_USER', 'HR')
    password = os.environ['ORACLE_PASSWORD']  # Required; never store credentials in source
    dsn = os.getenv('ORACLE_DSN', 'localhost:1521/XE')

    csv_path = r'data/processed/claim_procedures_processed.csv'

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    source_records = len(df)

    records = []
    for _, row in df.iterrows():
        # Retain the exact string format (e.g., 'PR4001')
        records.append((
            str(row['claim_procedure_id']),
            str(row['claim_id']),
            str(row['procedure_code']),
            str(row['procedure_type']),
            str(row['service_date']),
            int(row['units']),
            float(row['line_charge']),
        ))

    sql_insert = """
        INSERT INTO claim_procedures (
            claim_procedure_id,
            claim_id,
            procedure_code,
            procedure_type,
            service_date,
            units,
            line_charge
        ) VALUES (
            :1, :2, :3, :4, TO_DATE(:5, 'YYYY-MM-DD'), :6, :7
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

        print("========== PROCEDURE LOAD ==========")
        print(f"Source records: {source_records}")
        print(f"Records inserted: {inserted_count}")
        print("Target table: CLAIM_PROCEDURES")
        print("Load status: SUCCESS")
        print("====================================")

    except oracledb.Error as e:
        print("========== PROCEDURE LOAD ==========")
        print(f"Source records: {source_records}")
        print("Records inserted: 0")
        print("Target table: CLAIM_PROCEDURES")
        print("Load status: FAILED")
        print(f"Error Details: {e}")
        print("====================================")


if __name__ == '__main__':
    load_procedures_to_oracle()
