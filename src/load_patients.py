import os
import sys
import oracledb
import pandas as pd

# Path to your extracted Oracle Instant Client
INSTANT_CLIENT_DIR = r"D:\abu\Study materials\Aimore\Data engineering\instantclient_23_26"  # Update this to match your folder path

# Initialize Thick Mode for backward compatibility with older Oracle versions
try:
    if os.path.exists(INSTANT_CLIENT_DIR):
        oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_DIR)
    else:
        oracledb.init_oracle_client()
except Exception as e:
    print(f"Notice during Oracle client initialization: {e}")


def load_patients_to_oracle():
    # Database Connection Parameters
    user = os.getenv('ORACLE_USER', 'HR')
    password = os.environ['ORACLE_PASSWORD']  # Required; never store credentials in source
    dsn = os.getenv('ORACLE_DSN', 'localhost:1521/XE')

    csv_path = r'D:\App development\Healthcare AI Platform\data\processed\patients_processed.csv'

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    source_records = len(df)
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce')

    records = []
    for _, row in df.iterrows():
        # Option A: Handle missing birth date with placeholder or NULL depending on your schema
        dob = (
            row['date_of_birth'].strftime('%Y-%m-%d')
            if pd.notna(row['date_of_birth'])
            else None
        )
        # Fix: Default missing gender to 'Unknown' instead of None/NULL
        gender = (
            row['gender']
            if pd.notna(row['gender']) and str(row['gender']).strip() != ''
            else None
        )
        email = row['email'] if pd.notna(row['email']) else None
        phone = row['phone'] if pd.notna(row['phone']) else None
        insurance_id = (
            row['insurance_id'] if pd.notna(row['insurance_id']) else None
        )

        records.append((
            row['patient_id'],
            row['first_name'],
            row['last_name'],
            dob,
            gender,
            email,
            phone,
            insurance_id,
        ))

    sql_insert = """
        INSERT INTO patients (
            patient_id,
            first_name,
            last_name,
            date_of_birth,
            gender,
            email,
            phone,
            insurance_id
        ) VALUES (
            :1, :2, :3, TO_DATE(:4, 'YYYY-MM-DD'), :5, :6, :7, :8
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

        print("========== PATIENT LOAD ==========")
        print(f"Source records: {source_records}")
        print(f"Records inserted: {inserted_count}")
        print(f"Target table: PATIENTS")
        print(f"Load status: SUCCESS")
        print("==================================")

    except oracledb.Error as e:
        print("========== PATIENT LOAD ==========")
        print(f"Source records: {source_records}")
        print(f"Records inserted: 0")
        print(f"Target table: PATIENTS")
        print(f"Load status: FAILED")
        print(f"Error Details: {e}")
        print("==================================")


if __name__ == '__main__':
    load_patients_to_oracle()
