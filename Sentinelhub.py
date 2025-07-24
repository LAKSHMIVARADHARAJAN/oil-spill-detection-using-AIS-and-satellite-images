import requests
from requests.auth import HTTPBasicAuth

# Your Sentinel Hub credentials
CLIENT_ID = 'Your SentinelHub ClientID'
SECRET_KEY = 'Your Sentinelhub Secret_key'

# Define the API endpoint
API_URL = 'https://services.sentinel-hub.com/oauth/token'

# Prepare the authentication payload
payload = {
    'grant_type': 'client_credentials'
}

# Make the POST request to retrieve an access token
response = requests.post(API_URL, auth=HTTPBasicAuth(CLIENT_ID, SECRET_KEY), data=payload)

# Check the response status and retrieve the access token
if response.status_code == 200:
    access_token = response.json().get('access_token')
    print('Access Token:', access_token)
else:
    print('Failed to obtain access token:', response.status_code, response.text)
