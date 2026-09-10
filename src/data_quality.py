import re
import pandas as pd


def run_data_quality_checks(file_path):
    df = pd.read_csv(file_path)
    issues = []

    # 1. patient_id uniqueness
    duplicate_rows = df[df.duplicated(subset=['patient_id'], keep=False)]
    for _, row in duplicate_rows.iterrows():
        issues.append(
            {
                'patient_id': row['patient_id'],
                'field': 'patient_id',
                'rule': 'unique',
                'status': 'FAIL',
            }
        )

    # Required fields list
    required_fields = ['email', 'phone', 'insurance_id']

    # Regex patterns & validation rules
    email_pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
    phone_pattern = r'^\+?[\d-]{10,15}$'
    insurance_pattern = r'^INS-\d{5}$'
    allowed_genders = ['M', 'F']

    for _, row in df.iterrows():
        pid = row['patient_id']

        # 2. missing required fields
        for field in required_fields:
            val = row[field]
            if pd.isna(val) or str(val).strip() == '':
                issues.append(
                    {
                        'patient_id': pid,
                        'field': field,
                        'rule': 'required',
                        'status': 'FAIL',
                    }
                )

        # 3. valid date_of_birth
        dob = row['date_of_birth']
        if pd.notna(dob) and str(dob).strip() != '':
            try:
                pd.to_datetime(dob, format='%Y-%m-%d', errors='raise')
            except Exception:
                issues.append(
                    {
                        'patient_id': pid,
                        'field': 'date_of_birth',
                        'rule': 'valid_date',
                        'status': 'FAIL',
                    }
                )

        # 4. valid email format
        email = row['email']
        if pd.notna(email) and str(email).strip() != '':
            if not re.match(email_pattern, str(email)):
                issues.append(
                    {
                        'patient_id': pid,
                        'field': 'email',
                        'rule': 'valid_email_format',
                        'status': 'FAIL',
                    }
                )

        # 5. valid gender
        gender = row['gender']
        if pd.notna(gender) and str(gender).strip() != '':
            if gender not in allowed_genders:
                issues.append(
                    {
                        'patient_id': pid,
                        'field': 'gender',
                        'rule': 'allowed_gender',
                        'status': 'FAIL',
                    }
                )

        # 6. valid phone format
        phone = row['phone']
        if pd.notna(phone) and str(phone).strip() != '':
            if not re.match(phone_pattern, str(phone)):
                issues.append(
                    {
                        'patient_id': pid,
                        'field': 'phone',
                        'rule': 'valid_phone_format',
                        'status': 'FAIL',
                    }
                )

        # 7. valid insurance_id format
        insurance_id = row['insurance_id']
        if pd.notna(insurance_id) and str(insurance_id).strip() != '':
            if not re.match(insurance_pattern, str(insurance_id)):
                issues.append(
                    {
                        'patient_id': pid,
                        'field': 'insurance_id',
                        'rule': 'valid_insurance_format',
                        'status': 'FAIL',
                    }
                )

    # Convert results to DataFrame and remove duplicate failure entries
    report_df = pd.DataFrame(issues).drop_duplicates()

    # Print exact required output format
    for _, row in report_df.iterrows():
        print(
            f"{row['patient_id']} | {row['field']:<13} | {row['rule']:<18} | {row['status']}"
        )


if __name__ == '__main__':
    file_path = r'D:\App development\Healthcare AI Platform\data\raw\patients.csv'
    run_data_quality_checks(file_path)
