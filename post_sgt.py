import sys
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import ENV_VARS

# Disable insecure request warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Set Constants
HOST = ENV_VARS.HOST
PORT = ENV_VARS.PORT
USERNAME = ENV_VARS.USERNAME
PASSWORD = ENV_VARS.PASSWORD
HEADERS = {'Content-Type': "application/json", 'Accept': "application/json"}

# Check for exactly one argument passed to script (it's actually two cos script name counts as one!)
if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <new-sgt-name>")
    exit(1)

# Assign the argument to a variable
sgt_name = sys.argv[1]

# Encode the username and password to Base64 as required by the API
authentication = HTTPBasicAuth(USERNAME, PASSWORD)


def api_post(path, payload):
    response = requests.post(
        f"https://{HOST}:{PORT}{path}",
        headers=HEADERS,
        auth=authentication,
        data=payload,
        verify=False
    )
    if response.status_code != 201:
        print(response.raise_for_status())


def api_get(path):
    response = requests.get(
        f"https://{HOST}:{PORT}{path}",
        headers=HEADERS,
        auth=authentication,
        verify=False
    )
    if response.status_code != 200:
        print(response.raise_for_status())
    return response


#################################################################################################
# Create new SGT
#################################################################################################

# Create the Dictionary object (to be converted to a JSON structure)
sgt_json = {
    "Sgt": {
        "name": sgt_name,
        "value": -1
    }
}

# Set the URL
url = "/ers/config/sgt"

# Convert the dictionary to a JSON
body = json.dumps(sgt_json)

# Send the request to the API
api_post(url, body)

# Find the UUID of the new SGT
url = f"/ers/config/sgt?filter=name.EQ.{sgt_name}"
reply = api_get(url)
uuid = reply.json()["SearchResult"]["resources"][0]["id"]

# Print Confirmation including the UUID of the new SGT
print(f'\nNew SGT Created: "{sgt_name}", with UUID: "{uuid}"')


#################################################################################################
# Map the new SGT to the Exhibitors VN and IP Pool
#################################################################################################

# Set the variables
vn = "Exhibitors"
ip_pool = "100_98_0_0-Exhibitors"

# Create the Dictionary object (to be converted to a JSON structure)
sgt_vn_pool_json = {
    "SgtVNVlanContainer": {
        "sgtId": uuid,
        "virtualnetworklist": [
            {
                "name": vn,
                "vlans": [
                    {
                        "name": ip_pool,
                        "maxValue": 65536,
                        "data": "true"
                    }
                ]
            }
        ]
    }
}

# Set the URL for the API post
url = "/ers/config/sgtvnvlan"

# Convert the dictionary object created above, into a JSON construct
body = json.dumps(sgt_vn_pool_json)

# Post the data to the API
api_post(url, body)

# Print Confirmation
print('New SGT to VN to IP Pool relationship created:')
print(f'SGT:{sgt_name} --> VN:{vn} --> IP Pool:{ip_pool}')
