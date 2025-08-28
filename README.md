**Real-Time Oil Spill Detection System Using AIS Data and Satellite Imagery**
This project provides a comprehensive solution for detecting oil spills by analyzing vessel anomalies using AIS (Automatic Identification System) data and satellite imagery from Sentinel-1. It processes AIS data to identify unusual vessel behavior, fetches satellite images of the corresponding locations, and analyzes them for potential oil spills. If an oil spill is detected, an alert is generated.

Table of Contents
Features
Installation
Usage
Project Structure
Data Sources
Satellite Imagery
Deep Learning Detection
Alerts
License
Features
AIS Anomaly Detection: Uses Isolation Forest to detect abnormal vessel behavior based on AIS data (e.g., sudden changes in speed, course).
Satellite Imagery Retrieval: Automatically fetches Sentinel-1 satellite data for areas where anomalies were detected.
Oil Spill Detection: Processes satellite images to identify oil spill areas using pixel analysis.
Real-Time Alerts: Generates real-time email and SMS alerts if an oil spill is detected.
Installation
To run this project locally, follow these steps:

1. Clone the repository:
bash
Copy code
git clone https://github.com/DR-skcet/Oil-spill-Detection-using-AIS-Data-and-Satellite-Image.git
cd oil-spill-detection
2. Install required packages:
bash
Copy code
pip install -r requirements.txt
3. Set up environment variables:
Create a .env file in the root directory to store your API keys and credentials:

makefile
Copy code
SENTINEL_HUB_CLIENT_ID=your_client_id
SENTINEL_HUB_SECRET_KEY=your_secret_key
SMS_API_KEY=your_sms_api_key
EMAIL_API_KEY=your_email_api_key
4. Prepare the AIS Data:
Ensure you have the AIS data in AIS_data.csv file format with the following columns:

MMSI: Unique vessel identifier
BaseDateTime: Timestamp
SOG: Speed Over Ground
COG: Course Over Ground
LON: Longitude
LAT: Latitude
You can obtain AIS data from the following sources:

MarineTraffic
Vessel Finder
AIS Hub
Make sure your AIS data is formatted correctly before running the program.

5. Run the system:
Run the main script to begin AIS anomaly detection and trigger satellite oil spill analysis:

bash
Copy code
python main.py
Usage
Once the system is up and running, it will:

Continuously monitor and process the AIS data from AIS_data.csv.
Detect anomalies in vessel behavior using Isolation Forest.
For each anomaly, it will retrieve the corresponding Sentinel-1 satellite data.
Analyze the satellite image to detect any oil spills.
If an oil spill is detected, an alert will be sent via SMS and email.
Oil Spill Detection Example
The following image shows the process of detecting oil spills in an area identified by anomalous vessel activity.


Project Structure
bash
Copy code
.
├── main.py                 # Main script for AIS anomaly detection and triggering satellite data analysis
├── Sentinelhub.py          # Script to retrieve satellite images using Sentinel Hub API
├── deeplearning.py         # Image processing and deep learning model for oil spill detection
├── APIrequest.py           # Additional API handling for satellite data requests
├── AIS_data.csv            # Sample AIS data
├── requirements.txt        # Required Python packages
├── README.md               # This file
└── .env                    # Environment variables (API keys)
Data Sources
AIS Data
Automatic Identification System (AIS) data is used to track vessels' real-time positions and movements. Anomalies in this data may indicate dangerous or unusual behavior, such as erratic speed or unexpected stops. You can source AIS data from:

MarineTraffic
Vessel Finder
AIS Hub
Satellite Imagery
The system retrieves radar satellite images from the Sentinel-1 satellite via the Sentinel Hub API. Sentinel-1 data provides high-resolution radar images that can be processed to detect oil spills.

Deep Learning Detection
The deeplearning.py script processes the fetched satellite images and identifies areas of potential oil spills. The system uses image segmentation techniques to detect dark areas consistent with oil spill characteristics.

Alerts
If an oil spill is detected, the system generates real-time alerts. These alerts include:

SMS notifications via the configured SMS API.
Email notifications sent to designated recipients.
You can configure the recipients and the message content in the alert settings of the system.




