import requests
import pandas as pd
import ipaddress
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
# Server and authentication details
DNAInstance = 'https://100.100.100.100' ##Test DNA Instance(Change it to your DNA Instance)
username = 'YourUsername' ##Test DNA Username(Change it to your DNA Username)
password = 'yourPassword' ##Test DNA Password(Change it to your DNA Password)
all_devices=[]
requests.packages.urllib3.disable_warnings()
def get_api_token():
    global headers
    auth_rall_d = requests.post(f'{DNAInstance}/dna/system/api/v1/auth/token', auth=(username, password), verify=False)
    api_token = auth_rall_d.json().get('Token')
    if not api_token:
        raise Exception("Authentication failed, no token retrieved.")
    headers = {
        'X-Auth-Token': api_token,
        'Content-Type': 'application/json',
    }

get_api_token()

url = f"{DNAInstance}/dna/intent/api/v1/network-device"
start_index = 1
records_to_return = 500

while True:
        
    current_url = f"{url}/{start_index}/{records_to_return}"
    dev_response = requests.get(current_url, headers=headers, verify=False)
    response_json = dev_response.json()
    devices = response_json.get('response', [])
        
    if len(devices) == 0:
        break
    all_devices.extend(devices)
    start_index += records_to_return
    
All_DNA_Devices=pd.DataFrame(all_devices)
All_DNA_DevicesNA=All_DNA_Devices[['hostname','managementIpAddress','reachabilityStatus','type','series','id','family','deviceSupportLevel']]
All_DNA_DevicesNA = All_DNA_DevicesNA[(All_DNA_DevicesNA['hostname'].isna() & All_DNA_DevicesNA['reachabilityStatus'].str.contains('Unreachable', na=False)) |( All_DNA_DevicesNA['family'].str.contains('Unified AP', na=False) & All_DNA_DevicesNA['reachabilityStatus'].str.contains('Unreachable', na=False))| All_DNA_DevicesNA['type'].str.contains('Firewall', na=False) |All_DNA_DevicesNA['reachabilityStatus'].str.contains('Unknown', na=False) | All_DNA_DevicesNA['hostname'].isna() | All_DNA_DevicesNA['deviceSupportLevel'].str.contains('Unsupported', na=False) ]
print('Devices Removed')
print('------------------------------------------------------------------')
print(All_DNA_DevicesNA)
ID_todelete=All_DNA_DevicesNA['id'].tolist()
tot_dev=len(ID_todelete)
print(f'Total Devices Removed: {tot_dev}')
if tot_dev ==0:
    print('No devices to remove found')
else:
    for deleteid in ID_todelete:
        DNAcall=f'{DNAInstance}/dna/intent/api/v1/network-device/{deleteid}'
        print(f'Removing Device: {deleteid}')
        response = requests.delete(DNAcall, headers=headers, verify=False)
        res = response.json()
        print(res)