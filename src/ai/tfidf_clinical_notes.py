import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

input_path = r"data/processed/clinical_notes_processed.csv"

df = pd.read_csv(input_path)

vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(df["clean_text"])

print("========== TF-IDF REPRESENTATION ==========")
print()

print("Number of notes:", X.shape[0])
print("Number of features:", X.shape[1])

print()
print("Matrix shape:", X.shape)

print()
print("First 20 features:")
print(vectorizer.get_feature_names_out()[:20])

print()
print("===========================================")
