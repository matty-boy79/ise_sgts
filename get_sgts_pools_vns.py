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

authentication = HTTPBasicAuth(USERNAME, PASSWORD)
headers = {'Content-Type': "application/json", 'Accept': "application/json"}

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
print("All SGT to VN to IP Pool Relationships")
print("----------------------------------------------------------------\n")

relations = call_api("/ers/config/sgtvnvlan")
for relation in relations.json()["SearchResult"]["resources"]:
    #print(f'{relation["id"]}')
    specific_relation = call_api(f"/ers/config/sgtvnvlan/{relation['id']}")
    print(json.dumps(specific_relation.json(), indent=4))

#################################################################################################################
'''
print("\n----------------------------------------------------------------")
print("Relationship Details for one of 'em")
print("----------------------------------------------------------------\n")

specific_relation = call_api("/ers/config/sgtvnvlan/2daeea36-6b51-479a-96bd-54d2ed90087e")
print(json.dumps(specific_relation.json(), indent=4))
'''


#################################################################################################################


