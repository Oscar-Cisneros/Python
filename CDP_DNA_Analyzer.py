

#CDP Network Analyzer 



import requests
import pandas as pd
import ipaddress
import re
 
username = 'YourDNAUserName'
password = 'YourDNAPassword'
DNAInstance = 'https://100.100.100.100' ##Test DNA Instance(Change it to your DNA Instance)
 
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


Sitest_Info=Sitest_Info[Sitest_Info['Site Name'].str.contains('DesiredSiteName')] ## Edit This with your desired site name
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


#########################Getting the list of devices ###############################################3

Sites_Network_Devices['family']=Sites_Network_Devices['family'].fillna('')
Sites_Network_Devices=Sites_Network_Devices[Sites_Network_Devices['family'].str.contains('Switch')]
Sites_Network_Devices
Ipscdp=Sites_Network_Devices['IP'].tolist()
print(Ipscdp)

#############################################CDP neigh over the list of devices######################################
import paramiko
import time
import pandas as pd
import re

def execute_ssh_command(ip_address, usernames, passwords, commands):
    for username in usernames:
        for password in passwords:
            try:
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=ip_address, username=username, password=password, timeout=10)
                ssh_shell = ssh_client.invoke_shell()
                time.sleep(1)
                ssh_shell.recv(65535)
                
                output = ""
                for command in commands:
                    # Send the command
                    ssh_shell.send(command + "\n")
                    time.sleep(2)  # Adjust sleep time as needed
                    
                    # Wait for the command to execute and capture output
                    while ssh_shell.recv_ready():
                        output += ssh_shell.recv(65535).decode('utf-8')
                        time.sleep(1)
                
                return output.strip()
            
            except paramiko.AuthenticationException as auth_exc:
                print(f"Authentication failed for {ip_address} with username '{username}' and password '{password}': {str(auth_exc)}")
            except paramiko.SSHException as ssh_exc:
                print(f"SSH error occurred for {ip_address} with username '{username}' and password '{password}': {str(ssh_exc)}")
            except Exception as e:
                print(f"Error executing command on {ip_address} with username '{username}' and password '{password}': {str(e)}")
            finally:
                ssh_client.close()
    
    print(f"All username and password combinations failed for {ip_address}")
    return None


def parse_cdp_neighbors(output,device_ip):
    neighbors = []
    device_ids = re.findall(r"Device ID: (.+)", output)
    platforms = re.findall(r"Platform: (.+?),", output)
    interfaces = re.findall(r"Interface: (.+?),", output)
    ManamentIP = re.findall(r"IP address: (.+)", output)
    
    for device_id, platform, interface,ManamentIP in zip(device_ids, platforms, interfaces,ManamentIP):
        neighbor = {
            "Neighbor": device_id.strip(),
            "Platform": platform.strip(),
            "Interface": interface.strip(),
            "Interface IP": ManamentIP.strip(),
            "Device IP Address": device_ip
            
        }
        neighbors.append(neighbor)
    
    return neighbors

if __name__ == "__main__":
    usernames = ['DevicesUsername'] ## the username you use to connect to the device
    passwords = ['DevicesPassword']
    ip_addressesR = Ipscdp ## A list of Ip Addresses can be added to test this part of the script

  # List of IP addresses
    
    commands = [
        'terminal length 0',
        'show cdp nei detail',
    ]
    
    # Initialize an empty DataFrame
    cdpdevices = pd.DataFrame(columns=['Neighbor', 'Platform', 'Interface'])
    
    try:
        for ip_address in ip_addressesR:
            print(f"Connecting to {ip_address}...")
            output = execute_ssh_command(ip_address, usernames, passwords, commands)
            if output:
                print(f"Raw output from {ip_address}:")
                print(output)
                parsed_output = parse_cdp_neighbors(output,ip_address)
                print(f"Parsed output from {ip_address}:")
                print(parsed_output)
                for neighbor in parsed_output:
                    new_row = pd.DataFrame([neighbor])
                    cdpdevices = pd.concat([cdpdevices, new_row], ignore_index=True)
    
    except paramiko.AuthenticationException as auth_exc:
        print(f"Authentication failed: {str(auth_exc)}")
    except paramiko.SSHException as ssh_exc:
        print(f"SSH error occurred: {str(ssh_exc)}")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        print('Execution completed.')

isreachable=cdpdevices['Interface IP'].tolist()


######################################### Ping devices ########################################################################
import ping3
import threading
import pandas as pd
devices = isreachable

results = []

def ping_device(device):
    response = ping3.ping(device)
    if response is None:
        results.append({"IP": device, "Status": "Not Reachable"})
    else:
        results.append({"IP": device, "Status": "Reachable"})


threads = []
for device in devices:
    thread = threading.Thread(target=ping_device, args=(device,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
reachableDev = pd.DataFrame(results)


reachableDev

################ Getting the information of devices reachable and non reachable ###############################################3
summary=reachableDev.merge(cdpdevices,how='left',left_on='IP',right_on='Interface IP')
#summary=summary[['IP','Status','Neighbor','Platform','Device IP Address']]
new_names={'Neighbor':'Device Name','Device IP Address':'Parent IP Address'}
summary.rename(columns=new_names,inplace=True)
summary.drop_duplicates(subset=['IP','Device Name','Parent IP Address','Platform','Status','Interface'],inplace=True)
summary