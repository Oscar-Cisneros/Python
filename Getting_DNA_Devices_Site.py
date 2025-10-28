import requests
import pandas as pd
import ipaddress
import re
 
username = 'ossssss' ##Test User
password = '12345678' ## Test Password
DNAInstance = 'https://100.100.100.100' ## Test IP
 
# Suppress warnings for unverified HTTPS requests
requests.packages.urllib3.disable_warnings()
#Used Containers
all_devices=[]
Sites_Dataframe=[]
DNA_Devices=[]

# Authenticate and obtain the token
auth_rall_d = requests.post(f'{DNAInstance}/dna/system/api/v1/auth/token', auth=(username, password), verify=False)
api_token = auth_rall_d.json().get('Token')
 
 
if not api_token:
    raise Exception("Authentication failed, no token retrieved.")
 
# Set headers with the API token for authentication
headers = {
    'X-Auth-Token': api_token,
    'Content-Type': 'application/json',
}
 
DNADevicesCall = f"{DNAInstance}/dna/intent/api/v1/network-device"
DNASitesCall = f'{DNAInstance}/dna/intent/api/v1/site'
Sites_Information = requests.get(DNASitesCall, headers=headers, verify=False)
start_index = 1
records_to_return = 500
 
DNASites = Sites_Information.json()
Sites_df = pd.json_normalize(DNASites, 'response', errors='ignore')
 
 
 
while True:
       
    DevicesDNA = f"{DNADevicesCall}/{start_index}/{records_to_return}"
       
    dev_response = requests.get(DevicesDNA, headers=headers, verify=False)
    response_json = dev_response.json()
    devices = response_json.get('response', [])
       
    if len(devices) == 0:
        break
       
    all_devices.extend(devices)
    start_index += records_to_return
 
required_attributes = ['name', 'id']
if all(column in Sites_df.columns for column in required_attributes):
  Sites_df = Sites_df[required_attributes]
  Sites_df.columns = ['Site Name', 'ID']
  Sites_Dataframe.append(Sites_df)
 
Sitest_Info = pd.concat(Sites_Dataframe, ignore_index=True)
 
Sitest_Info['only site']=Sitest_Info['Site Name'].str.split('(').str[0].str.strip()
#Sitest_Info=Sitest_Info[~Sitest_Info['only site'].str.contains('|'.join(Search))]
Sitest_Info

#Change the site
Sitest_Info=Sitest_Info[Sitest_Info['Site Name'].str.contains('DesiredSiteFromDNA')]
Sitest_Info
codes=Sitest_Info['ID'].tolist()
for siteid in codes:
    API_Site_Members = f'{DNAInstance}/dna/intent/api/v1/membership/{siteid}'
    Devices_response = requests.get(API_Site_Members, headers=headers, verify=False)
   
    if Devices_response.status_code == 200:
        DNASites = Devices_response.json()
        Sites_df_devices = pd.json_normalize(DNASites['device'], 'response', errors='ignore')
        required_attributes_devices = ['hostname', 'managementIpAddress', 'macAddress', 'serialNumber', 'instanceUuid','family']
        if all(column in Sites_df_devices.columns for column in required_attributes_devices):
            Sites_df_devices = Sites_df_devices[required_attributes_devices]
            Sites_df_devices.columns = ['Hostname', 'IP', 'MAC', 'SN', 'DeviceID','family']
            Sites_df_devices['SiteID'] = siteid
            DNA_Devices.append(Sites_df_devices)
           
Sites_Network_Devices=pd.concat(DNA_Devices, ignore_index=True)
Sites_Network_Devices=pd.DataFrame(Sites_Network_Devices)