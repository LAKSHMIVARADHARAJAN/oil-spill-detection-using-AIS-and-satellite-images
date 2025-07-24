import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
from math import radians, cos, sin, asin, sqrt
from sklearn.metrics import accuracy_score

# Define the Haversine function to calculate the distance between two points on Earth
def haversine(lon1, lat1, lon2, lat2):
    # Check for NaN values before performing calculations
    if pd.isnull(lon1) or pd.isnull(lat1) or pd.isnull(lon2) or pd.isnull(lat2):
        return np.nan
    
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r
    
# Load the AIS data (replace 'Ais_sample.csv' with your actual file path)
ais_data = pd.read_csv('Ais_sample.csv', dtype={'ColumnName': 'str'}, low_memory=False)

# Display the first few rows of the dataset
print("Initial Data:\n", ais_data.head())

# Check for missing values and handle them appropriately
missing_values = ais_data.isnull().sum()
print("\nMissing Values:\n", missing_values)

# Drop rows with missing values (if any)
ais_data = ais_data.dropna()

# Convert the 'BaseDateTime' column to datetime format
ais_data['BaseDateTime'] = pd.to_datetime(ais_data['BaseDateTime'], errors='coerce')

# Ensure there are no NaT values in 'BaseDateTime' after conversion
ais_data = ais_data.dropna(subset=['BaseDateTime'])

# Sort the data by 'MMSI' and 'BaseDateTime' to ensure it's in the correct order
ais_data = ais_data.sort_values(by=['MMSI', 'BaseDateTime']).reset_index(drop=True)

# Calculate the change in Speed Over Ground (SOG) and Course Over Ground (COG)
ais_data['delta_sog'] = ais_data.groupby('MMSI')['SOG'].diff().fillna(0)
ais_data['delta_cog'] = ais_data.groupby('MMSI')['COG'].diff().fillna(0)

# Calculate distance traveled between consecutive points using the Haversine function
ais_data['prev_lon'] = ais_data.groupby('MMSI')['LON'].shift()
ais_data['prev_lat'] = ais_data.groupby('MMSI')['LAT'].shift()
ais_data['Distance_Traveled'] = ais_data.apply(
    lambda row: haversine(row['prev_lon'], row['prev_lat'], row['LON'], row['LAT']), axis=1
).fillna(0)

# Display the data with the new features
print("\nData with New Features:\n", ais_data.head())

# Select features for anomaly detection
features = ['SOG', 'COG', 'delta_sog', 'delta_cog', 'Distance_Traveled']

# Initialize the Isolation Forest model
model = IsolationForest(contamination=0.01, random_state=42)

# Fit the model and predict anomalies
ais_data['anomaly'] = model.fit_predict(ais_data[features])

# -1 indicates an anomaly, 1 indicates normal behavior
print("\nAnomaly Counts:\n", ais_data['anomaly'].value_counts())

# Filter out the anomalies for further analysis
anomalies = ais_data[ais_data['anomaly'] == -1]

# Plot Speed Over Ground (SOG) with anomalies highlighted
plt.figure(figsize=(14, 7))
plt.plot(ais_data['BaseDateTime'], ais_data['SOG'], label='SOG', color='blue')
plt.scatter(anomalies['BaseDateTime'], anomalies['SOG'], color='red', label='Anomalies')
plt.xlabel('Timestamp')
plt.ylabel('Speed Over Ground (SOG)')
plt.title('Anomaly Detection in AIS Data (Speed Over Ground)')
plt.legend(loc='upper right')  # Explicitly specify a location for the legend
plt.show()

# Display detected anomalies with their details
print("\nDetected Anomalies:\n", anomalies[['MMSI', 'BaseDateTime', 'SOG', 'COG', 'delta_sog', 'delta_cog', 'Distance_Traveled']])

