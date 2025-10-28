import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd
from io import StringIO

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


prtg_server = "YourServer"  
username = "YourUserName"  
passhash = "YourPasHas"  


sensors_url = f"https://{prtg_server}/api/table.csv?content=sensors&columns=objid,group,device,sensor,status,lastvalue,message&filter_status=5&filter_status=4&username={username}&passhash={passhash}"

devices_url = f"https://{prtg_server}/api/table.csv?content=devices&columns=objid,device,host,ip&username={username}&passhash={passhash}"


sensors_response = requests.get(sensors_url, verify=False)
sensors_data = sensors_response.content.decode('utf-8')
devices_response = requests.get(devices_url, verify=False)
devices_data = devices_response.content.decode('utf-8')
sensors_df = pd.read_csv(StringIO(sensors_data))
devices_df = pd.read_csv(StringIO(devices_data))

def extract_device_name(text):
    # Regex to match MCAIN-{Whatever}-{Whatever} pattern not surrounded by []
    matches = re.findall(r'\bDesiredPattern-[A-Z0-9]+-[A-Z0-9]+\b', text)
    # Filter out matches that are inside square brackets
    return [match for match in matches if not re.search(r'\[.*?\b' + re.escape(match) + r'\b.*?\]', text)]



PRTGInfo=sensors_df.merge(devices_df,how='left',on='Device')
PRTGDevices=PRTGInfo[['Group','Host','Device','Device(RAW)_x','Group(RAW)','Sensor','Status','Message(RAW)']]
PRTGDevices['Site']=PRTGDevices['Group(RAW)'].str.split(' ').str[0]
PRTGDevices['Device Only'] = PRTGDevices['Device'].apply(extract_device_name)
PRTGDevices = PRTGDevices.explode('Device Only').reset_index(drop=True)
Reach = PRTGDevices['Host'].tolist()
Reach = [str(item) for item in Reach]
reach_str = ', '.join(Reach)
Reach_list = [ip.strip() for ip in reach_str.split(',')]
print(Reach_list)
print(reach_str)
Runique=list(set(Reach_list))
print(len(Runique))