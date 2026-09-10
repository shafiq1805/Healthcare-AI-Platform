import pandas as pd

df = pd.read_csv(r"D:\App development\Healthcare AI Platform\data\raw\patients.csv")

allowed_genders = ['M', 'F']

# Check for invalid gender values
invalid_gender_rows= df[~df['gender'].isin(allowed_genders)]

# Print output in the requested format
print("========== GENDER VALIDATION ==========\n")
print("Allowed values:")
print(allowed_genders)
print("\nInvalid gender records:\n")
print(invalid_gender_rows[["patient_id", "gender"]].to_string(index=False))
print(f"\nTotal records: {len(df)}")
print(f"Invalid gender records: {len(invalid_gender_rows)}")
print("\n========================================")
