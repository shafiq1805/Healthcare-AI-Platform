import pandas as pd

df = pd.read_csv(r"D:\App development\Healthcare AI Platform\data\raw\patients.csv")

#Missing values per column

print("Missing values per column:\n", df.isnull().sum())

#Duplicate rows in the dataset

print("Duplicate patient IDs:\n", df[df.duplicated(subset='patient_id', keep=False)])

#Unique values in each column

print(df['gender'].unique())

#total number od unque patients

print("Total number of unique patients:", df['patient_id'].nunique())

# Convert date_of_birth column to datetime, forcing invalid values to NaT
df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce')

# Inspect converted records
print(df[['patient_id', 'first_name', 'last_name', 'date_of_birth']])

# Identify rows with invalid dates (now marked as NaT)
invalid_dob_rows = df[df['date_of_birth'].isna()]
print("\nRows with invalid dates:\n", invalid_dob_rows[['patient_id', 'first_name', 'last_name']])


#Missing emails
missing_emails = df[df['email'].isnull()]

#invalid emails
invalid_emails = df[~df['email'].str.contains(r'^[\w\.-]+@[\w\.-]+\.\w+$', na=True)]
print(invalid_emails[['patient_id','email']])
print(F'Total reecords: {len(df)}')
print('Missing emails:', len(missing_emails))
print('Invalid emails:', len(invalid_emails))
