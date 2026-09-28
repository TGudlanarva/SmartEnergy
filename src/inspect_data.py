import pandas as pd

# Load the dataset
file_path = "data/Indias_Electricity_Consumption_Dataset.csv"

df = pd.read_csv(file_path)

print("===== DATASET SHAPE =====")
print(df.shape)

print("\n===== COLUMN NAMES =====")
print(df.columns.tolist())

print("\n===== DATA INFORMATION =====")
df.info()

print("\n===== MISSING VALUES =====")
print(df.isnull().sum())

print("\n===== FIRST 5 ROWS =====")
print(df.head())

print("\n===== STATISTICAL SUMMARY =====")
print(df.describe())