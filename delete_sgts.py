import datetime
import time
import sys
import ENV_VARS
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
HEADERS = {'Content-Type': "application/json", 'Accept': "application/json"}
LOGFILE = ENV_VARS.LOGFILE

# Check for exactly one argument passed to script (it's actually two cos script name counts as one!)
if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <Start of SGT name to delete>")
    exit(1)

# Assign the argument to a variable
search_filter = sys.argv[1]

authentication = HTTPBasicAuth(USERNAME, PASSWORD)


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


def api_delete(uuid):
    response = requests.delete(
        f"https://{HOST}:{PORT}/ers/config/sgt/{uuid}",
        headers=HEADERS,
        auth=authentication,
        verify=False
    )
    if response.status_code != 204:
        print(response.raise_for_status())
    return response


sgt_dict = {}
sgts = api_get(f"/ers/config/sgt?filter=name.STARTSW.{search_filter}&size=100")
sgt_count = sgts.json()["SearchResult"]["total"]
if sgt_count == 0:
    print("No SGTs match your string. Exiting")
    exit()

print("Matching SGTs")
print("=============")
for sgt in sgts.json()["SearchResult"]["resources"]:
    print(sgt["name"])
    sgt_dict[sgt["id"]] = sgt["name"]

choice = input('Are you sure you want to delete all these SGTs? [y/n] ')
if choice == 'y' or choice == 'Y':
    # Get current time to measure how long it takes to delete the SGTs
    start = time.perf_counter()
    for sgt_uuid in sgt_dict:
        sgt_name = sgt_dict[sgt_uuid]
        api_delete(sgt_uuid)
        print(f"{sgt_name} DELETED!")

        # Update log file
        now = datetime.datetime.now()
        log = open(LOGFILE, "a")
        log.write(f"{now} Deleted SGT {sgt_name} with UUID {sgt_uuid}\n")
        log.close()

else:
    print('No changes made.')

# Get current time again, subtract the start time and print message
finish = time.perf_counter()
diff = finish - start
print("\n-----------------------------------------")
print(f"Deleted {sgt_count} SGTs in {int(diff)} seconds.")
