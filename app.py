
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from math import radians, cos, sin, sqrt, atan2
import base64

st.set_page_config(page_title="Oil Spill & Anomaly Detection", layout="wide")
st.title("🚢 AIS Data Analysis and Anomaly Detection")

# Upload CSV file
uploaded_file = st.file_uploader("Upload AIS CSV file", type="csv")

if uploaded_file is not None:
    ais_data = pd.read_csv(uploaded_file)

    # Show data
    st.subheader("Raw AIS Data")
    st.dataframe(ais_data.head())

    # Ensure required columns exist
    required_columns = ['MMSI', 'Timestamp', 'Latitude', 'Longitude', 'Speed', 'Heading']
    if not all(col in ais_data.columns for col in required_columns):
        st.error("CSV must contain these columns: " + ", ".join(required_columns))
    else:
        # Rename columns for uniformity
        ais_data.rename(columns={
            'Latitude': 'LAT',
            'Longitude': 'LON',
            'Speed': 'SOG',
            'Heading': 'COG'
        }, inplace=True)

        # Convert Timestamp to datetime
        ais_data['Timestamp'] = pd.to_datetime(ais_data['Timestamp'], errors='coerce')
        ais_data = ais_data.dropna(subset=['Timestamp'])
        ais_data = ais_data.sort_values(by=['MMSI', 'Timestamp']).reset_index(drop=True)

        # Haversine distance
        def haversine(lon1, lat1, lon2, lat2):
            if pd.isna(lon1) or pd.isna(lat1) or pd.isna(lon2) or pd.isna(lat2):
                return 0
            R = 6371.0
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            return R * 2 * atan2(sqrt(a), sqrt(1 - a))

        # Feature engineering
        ais_data['delta_sog'] = ais_data.groupby('MMSI')['SOG'].diff().fillna(0)
        ais_data['delta_cog'] = ais_data.groupby('MMSI')['COG'].diff().fillna(0)
        ais_data['prev_lon'] = ais_data.groupby('MMSI')['LON'].shift()
        ais_data['prev_lat'] = ais_data.groupby('MMSI')['LAT'].shift()
        ais_data['Distance_Traveled'] = ais_data.apply(
            lambda row: haversine(row['prev_lon'], row['prev_lat'], row['LON'], row['LAT']), axis=1
        )

        # Model
        features = ['SOG', 'COG', 'delta_sog', 'delta_cog', 'Distance_Traveled']
        model = IsolationForest(contamination=0.01, random_state=42)
        ais_data['anomaly'] = model.fit_predict(ais_data[features])

        # Plot
        st.subheader("Speed Over Ground (SOG) with Anomalies")
        anomalies = ais_data[ais_data['anomaly'] == -1]
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(ais_data['Timestamp'], ais_data['SOG'], label='SOG', color='blue')
        ax.scatter(anomalies['Timestamp'], anomalies['SOG'], color='red', label='Anomalies')
        ax.set_xlabel('Timestamp')
        ax.set_ylabel('Speed Over Ground (SOG)')
        ax.set_title('Anomaly Detection in AIS Data')
        ax.legend()
        st.pyplot(fig)

        # Show anomalies
        st.subheader("Detected Anomalies")
        st.dataframe(anomalies[['MMSI', 'Timestamp', 'SOG', 'COG', 'delta_sog', 'delta_cog', 'Distance_Traveled']])

        # Option to download anomaly CSV
        csv = anomalies.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="anomalies.csv">📥 Download Anomalies as CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
else:
    st.info("Please upload a CSV file containing AIS data to proceed.")
