import datetime
import sys
import json
import time
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import ENV_VARS

# Get current time to measure how long it takes to complete
start = time.perf_counter()

# Disable insecure request warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Set Constants
HOST = ENV_VARS.HOST
PORT = ENV_VARS.PORT
USERNAME = ENV_VARS.USERNAME
PASSWORD = ENV_VARS.PASSWORD
LOGFILE = ENV_VARS.LOGFILE
HEADERS = {'Content-Type': "application/json", 'Accept': "application/json"}

# Check for exactly one argument passed to script (it's actually two cos script name counts as one!)
if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <filename_to_read_SGTs_from>")
    exit(1)

# Assign the argument to a variable
filename = sys.argv[1]

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


sgt_counter = 0

# Loop through each row of the data file, creating SGTs
with open(filename) as data:
    for sgt_name_with_newline_char in data:
        sgt_name = sgt_name_with_newline_char.strip()

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

        # Update log file
        now = datetime.datetime.now()
        log = open(LOGFILE, "a")
        log.write(f"{now} Created SGT {sgt_name} with UUID {uuid}\n")
        log.close()

        # Print Confirmation including the UUID of the new SGT
        print(f'\nSGT Created: "{sgt_name}", with UUID: "{uuid}"')

        # Increment counter
        sgt_counter += 1


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
        print(f'Relationship created: "SGT:{sgt_name} --> VN:{vn} --> IP Pool:{ip_pool}"')

# Get current time again, subtract the start time and print message
finish = time.perf_counter()
diff = finish - start
print("\n-----------------------------------------")
print(f"Created {sgt_counter} SGTs in {int(diff)} seconds.")
