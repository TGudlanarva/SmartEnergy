import pandas as pd

# Load dataset
file_path = "data/Indias_Electricity_Consumption_Dataset.csv"
df = pd.read_csv(file_path)

print("Original shape:", df.shape)

# Remove unnecessary index column
df = df.drop(columns=["Unnamed: 0"])

# Convert Dates from text to datetime
df["Dates"] = pd.to_datetime(df["Dates"])

# Sort by date
df = df.sort_values("Dates")

# Display date range
print("\nDate range:")
print("Start:", df["Dates"].min())
print("End:", df["Dates"].max())

# Create date-based features
df["Year"] = df["Dates"].dt.year
df["Month"] = df["Dates"].dt.month
df["Day"] = df["Dates"].dt.day
df["Day_of_Week"] = df["Dates"].dt.dayofweek

print("\nNew shape:", df.shape)

print("\nFirst 5 rows:")
print(df.head())