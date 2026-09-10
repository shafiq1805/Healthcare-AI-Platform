import pandas as pd


#phone validation
invalid_phone_rows = df[df['phone'].isna() | (df['phone']=='')]

print("========== CONTACT VALIDATION ==========\n")
print("Invalid phone records:")
print(invalid_phone_rows[['patient_id', 'phone']].to_string(index=False))

#Insurance validation
invalid_insurance_rows = df[df['insurance_id'].isna() | (df['insurance_id']=='')]

print("Missing Insurance IDs:")
print(invalid_insurance_rows[['patient_id', 'insurance_id']].to_string(index=False))

print(df[["patient_id", "phone", "insurance_id"]].to_string(index=False))
