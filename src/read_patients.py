import pandas as pd

df = pd.read_csv(r"D:\App development\Healthcare AI Platform\data\raw\patients.csv")

print("Number of rows in the dataset:", len(df))
print("Number of columns in the dataset:", len(df.columns))
print("\nColumn names:",list(df.columns))
print("\nData types:", (df.dtypes))
print("\nFirst 5 rows of the dataset:\n", df.head())

print("\nSummary statistics of the dataset:\n", df.describe())
