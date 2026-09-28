import pandas as pd

# Load original dataset
df = pd.read_csv("data/Indias_Electricity_Consumption_Dataset.csv")

# Remove unnecessary index column
df = df.drop(columns=["Unnamed: 0"])

# Convert date
df["Dates"] = pd.to_datetime(df["Dates"])

# These are not states, so exclude them for now
exclude_columns = [
    "Dates",
    "Total Consumption",
    "DVC",
    "Essar steel",
    "DD",
    "DNH"
]

# Select state/UT columns
state_columns = [
    col for col in df.columns
    if col not in exclude_columns
]

# Convert wide data to long data
long_df = df.melt(
    id_vars=["Dates"],
    value_vars=state_columns,
    var_name="State",
    value_name="Consumption"
)

# Sort each state's records by date
long_df = long_df.sort_values(
    ["State", "Dates"]
).reset_index(drop=True)

print("New dataset shape:")
print(long_df.shape)

print("\nFirst 10 rows:")
print(long_df.head(10))

print("\nNumber of states/UTs:")
print(long_df["State"].nunique())

print("\nStates/UTs:")
print(long_df["State"].unique())

print("\nMissing consumption values:")
print(long_df["Consumption"].isnull().sum())