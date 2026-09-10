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


def load_claims_to_oracle():
    # Database Connection Parameters
    user = os.getenv('ORACLE_USER', 'HR')
    password = os.environ['ORACLE_PASSWORD']  # Required; never store credentials in source
    dsn = os.getenv('ORACLE_DSN', 'localhost:1521/XE')

    csv_path = r'data/processed/claims_processed.csv'

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    source_records = len(df)

    # Convert service_date to standard string format for SQL TO_DATE conversion
    df['service_date'] = pd.to_datetime(df['service_date'], errors='coerce')

    records = []
    for _, row in df.iterrows():
        service_date = (
            row['service_date'].strftime('%Y-%m-%d')
            if pd.notna(row['service_date'])
            else None
        )

        records.append((
            row['claim_id'],
            row['patient_id'],
            service_date,
            row['provider_id'],
            row['payer'],
            row['claim_status'],
            float(row['total_charge']),
        ))

    sql_insert = """
        INSERT INTO claims (
            claim_id,
            patient_id,
            service_date,
            provider_id,
            payer,
            claim_status,
            total_charge
        ) VALUES (
            :1, :2, TO_DATE(:3, 'YYYY-MM-DD'), :4, :5, :6, :7
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

        print("========== CLAIM LOAD ==========")
        print(f"Source records: {source_records}")
        print(f"Records inserted: {inserted_count}")
        print("Target table: CLAIMS")
        print("Load status: SUCCESS")
        print("================================")

    except oracledb.Error as e:
        print("========== CLAIM LOAD ==========")
        print(f"Source records: {source_records}")
        print("Records inserted: 0")
        print("Target table: CLAIMS")
        print("Load status: FAILED")
        print(f"Error Details: {e}")
        print("================================")


if __name__ == '__main__':
    load_claims_to_oracle()
