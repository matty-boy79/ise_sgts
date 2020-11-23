import ENV_VARS
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable insecure request warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Set Constants
HOST = ENV_VARS.HOST
PORT = ENV_VARS.PORT
USERNAME = ENV_VARS.USERNAME
PASSWORD = ENV_VARS.PASSWORD

authentication = HTTPBasicAuth(username, password)
headers = {'Content-Type': "application/json",'Accept': "application/json"}

def call_api(path):
    response = requests.get(
        f"https://{host}:{port}{path}",
        headers=headers,
        auth=authentication,
        verify=False,
    )
    #print(response.raise_for_status())
    return response

#################################################################################################################

print("\n----------------------------------------------------------------")
print("All SGT UUIDs and Names")
print("----------------------------------------------------------------\n")

sgts = call_api("/ers/config/sgt")
for sgt in sgts.json()["SearchResult"]["resources"]:
    print(f'{sgt["id"]} | {sgt["name"]}')

#################################################################################################################

print("\n----------------------------------------------------------------")
print("SGT Details for BMW")
print("----------------------------------------------------------------\n")

specific_sgt = call_api("/ers/config/sgt?filter=name.STARTSW.BMW")
print(json.dumps(specific_sgt.json(), indent=4))

#################################################################################################################


