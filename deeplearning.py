import requests
import yagmail
from twilio.rest import Client
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
import webbrowser
import os

# Twilio configuration
account_sid = 'Your account_sid'
auth_token = 'Your auth_token'
twilio_number = 'Twillio phone number'
recipient_number = 'Recipient phone number'

# Define bounding box coordinates for the Mumbai region
longitude_min = 72.6
longitude_max = 73.0
latitude_min = 18.8
latitude_max = 19.3

# Set your access token here
access_token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ3dE9hV1o2aFJJeUowbGlsYXctcWd4NzlUdm1hX3ZKZlNuMW1WNm5HX0tVIn0.eyJleHAiOjE3MjUwOTU3NDUsImlhdCI6MTcyNTA5MjE0NSwianRpIjoiZTNlMWEzZDQtMjFmZi00OGY5LWFjYTctMTdhMzY2ODNiNzQyIiwiaXNzIjoiaHR0cHM6Ly9zZXJ2aWNlcy5zZW50aW5lbC1odWIuY29tL2F1dGgvcmVhbG1zL21haW4iLCJzdWIiOiJhN2Q2NTc0Zi04YjFjLTQ2NDEtOWY3Yi00OGUzMzE3ZDhkODEiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiIyOGY4YzQ3ZC04ZDU1LTQxNTEtODliYy01NjhjYjJhZTgyNmQiLCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJjbGllbnRIb3N0IjoiMTUyLjU4LjI0OS4xNjgiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInByZWZlcnJlZF91c2VybmFtZSI6InNlcnZpY2UtYWNjb3VudC0yOGY4YzQ3ZC04ZDU1LTQxNTEtODliYy01NjhjYjJhZTgyNmQiLCJjbGllbnRBZGRyZXNzIjoiMTUyLjU4LjI0OS4xNjgiLCJjbGllbnRfaWQiOiIyOGY4YzQ3ZC04ZDU1LTQxNTEtODliYy01NjhjYjJhZTgyNmQiLCJhY2NvdW50IjoiNWZlODk2ZGYtYjBlOC00NzliLTg5NjgtMGEwMDkzMjlhZDhlIn0.lyo9ZVsVR4CZiKfuLKcsGjsyKJPx5ZmkYhzcDekc_MzKAwGUnJzXkSg6kalR2Uqld8V8lalH-kU3CbBAqCA0Gli8PECIWYyxATxuIISIzpH3EPoQUu4s3I90xaEQZo6wSnr5oNiVc_aUs5ofVSkwN6Mw-iyLANxgAWsJVJS-2tdy7a0o6rbQSMAeTWNPbykUUh8G8wutlbjh3VcY4S8k2wEk2i7bdP4d94NEGSDWdVgCfXhtnKspySY_CJFfNn-k7DGBrhlg6i-gannnUL_Z-wg-K7AaoFmz999yqAShoF01PJ-BnbPc1xLta2CgYD8O0T8nH0jpHOOvEWRN2-dBtA"

# Define the Sentinel Hub API endpoint for Sentinel-1 data
url = "https://services.sentinel-hub.com/api/v1/process"

# Define headers for the request
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Define the request payload for oil spill detection (using Sentinel-1)
payload = {
    "input": {
        "bounds": {
            "bbox": [longitude_min, latitude_min, longitude_max, latitude_max],
            "properties": {
                "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
            }
        },
        "data": [
            {
                "type": "S1GRD",
                "dataFilter": {
                    "timeRange": {
                        "from": "2023-01-01T00:00:00Z",
                        "to": "2023-04-01T23:59:59Z"
                    }
                }
            }
        ]
    },
    "output": {
        "width": 2056,
        "height": 2056,
        "responses": [
            {
                "identifier": "default",
                "format": {
                    "type": "image/png"
                }
            }
        ]
    },
    "evalscript": """
    //VERSION=3
    function setup() {
        return {
            input: ["VV"],
            output: { bands: 1 }
        };
    }

    function evaluatePixel(sample) {
        // Threshold value (adjust based on observation)
        var threshold = 0.05;

        // Oil spill detection based on VV backscatter
        if (sample.VV < threshold) {
            return [1];  // Oil spill (highlighted in white)
        } else {
            return [0];  // Non-oil spill (black background)
        }
    }
    """
}

# Function to send email alerts
def send_email_alert(subject, body, attachment):
    yag = yagmail.SMTP("mail_id", "App password")
    yag.send(to="recipient mail_id", subject=subject, contents=body, attachments=attachment)
    print("Email sent!")

# Function to send SMS alerts
def send_sms_alert(body):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=body,
        from_=twilio_number,
        to=recipient_number
    )
    print(f"SMS sent! SID: {message.sid}")

# Function to generate PDF report
def generate_pdf_report(latitude, longitude, vessel_info, spill_area, timestamp, image_file, pdf_file):
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    styles = getSampleStyleSheet()
    
    elements = []

    title = f"Oil Spill Incident Report - {timestamp}"
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))

    incident_details = f"""
    <b>Details:</b><br/>
    <b>Latitude:</b> {latitude}<br/>
    <b>Longitude:</b> {longitude}<br/>
    <b>Vessel Information:</b> {vessel_info}<br/>
    <b>Spill Area:</b> {spill_area}<br/>
    <b>Detection Time:</b> {timestamp}<br/>
    """
    elements.append(Paragraph(incident_details, styles['BodyText']))
    elements.append(Spacer(1, 12))

    # Insert the image of the oil spill detection
    elements.append(Image(image_file, width=400, height=400))
    elements.append(Spacer(1, 12))

    doc.build(elements)
    print(f"PDF report generated: {pdf_file}")

# Function to open the PDF file
def open_pdf_file(pdf_file):
    webbrowser.open_new(pdf_file)
    print(f"PDF report opened: {pdf_file}")

# Make the API request
response = requests.post(url, headers=headers, json=payload)

# Check if the request was successful
if response.status_code == 200:
    # Save the image to a file
    image_file = "oil_spill_detection_mumbai.png"
    with open(image_file, "wb") as f:
        f.write(response.content)
    
    # Example: If oil spill is detected
    oil_spill_detected = True  # Replace with actual detection logic

    if oil_spill_detected:
        # Sample latitude, longitude, and vessel information (replace with actual data)
        latitude = 19.0
        longitude = 72.8
        vessel_info = "Vessel 73"
        spill_area = "234 square meters"  # Replace with actual calculated area
        timestamp = "2024-01-07 10:30 UTC"  # Replace with actual timestamp

        email_body = f"""
        An oil spill has been detected in the Mumbai region.

        **Details:**
        - **Latitude:** {latitude}
        - **Longitude:** {longitude}
        - **Vessel Information:** {vessel_info}
        - **Spill Area:** {spill_area}
        - **Detection Time:** {timestamp}

        **Location:**
        The spill was detected within the coordinates of {latitude}, {longitude} in the Mumbai region.

        **Vessel Info:**
        The vessel {vessel_info} was identified in the vicinity at the time of detection. Further investigation is recommended.

        **Recommended Actions:**
        - Immediate containment of the spill to prevent environmental damage.
        - Notify nearby vessels to avoid the area.
        - Begin cleanup operations in coordination with local authorities.

        Please review the attached image for further details.
        """

        send_email_alert(
            subject="Urgent: Oil Spill Detected in Mumbai Region",
            body=email_body,
            attachment=image_file
        )

        sms_body = f"""
        Oil Spill Alert in Mumbai Region:
        Latitude: {latitude}
        Longitude: {longitude}
        Vessel: {vessel_info}
        Spill Area: {spill_area}

        Check your email for details.
        """

        send_sms_alert(body=sms_body)

        # Generate PDF report
        pdf_file = "Oil_Spill_Incident_Report.pdf"
        generate_pdf_report(latitude, longitude, vessel_info, spill_area, timestamp, image_file, pdf_file)


else:
    print(f"Failed to retrieve data: {response.status_code} - {response.text}")
