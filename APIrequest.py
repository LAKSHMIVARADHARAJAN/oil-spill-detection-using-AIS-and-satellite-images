import os
import requests

# Define bounding box coordinates for the Gulf of Mexico
longitude_min = 71.5  # Western boundary
longitude_max = 73.5  # Eastern boundary
latitude_min = 18.5  # Southern boundary
latitude_max = 19.5 # Northern boundary

# Set your access token (ideally from an environment variable)
access_token = os.getenv("SENTINEL_HUB_ACCESS_TOKEN", "Your Access Token")

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
                        "to": "2023-01-31T23:59:59Z"
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
            input: ["VV", "VH"],
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

# Make the API request
response = requests.post(url, headers=headers, json=payload)

# Check if the request was successful
if response.status_code == 200:
    # Save the image to a file with a dynamic name
    filename = f"oil_spill_detection_mumbai_{longitude_min}_{latitude_min}.png"
    with open(filename, "wb") as f:
        f.write(response.content)
    print(f"Image saved as {filename}")
else:
    print(f"Failed to retrieve data: {response.status_code} - {response.text}")
