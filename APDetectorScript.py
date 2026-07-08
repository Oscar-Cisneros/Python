import paramiko
import time
import pandas as pd
import re

def execute_ssh_command(ip_address, username, password, commands):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=ip_address, username=username, password=password, timeout=10)
        ssh_shell = ssh_client.invoke_shell()
        time.sleep(1)
        ssh_shell.recv(65535)  # Clear initial buffer
        
        output = ""
        for command in commands:
            ssh_shell.send(command + "\n")
            time.sleep(2)  # Adjust sleep time as needed
            
            while True:
                if ssh_shell.recv_ready():
                    new_data = ssh_shell.recv(65535).decode('utf-8', 'ignore')
                    output += new_data
                    # Check if pagination prompt is present
                    if re.search(r"--More--", new_data):
                        ssh_shell.send(" ")  # Send space to continue
                        time.sleep(1)  # Adjust sleep time as needed
                    else:
                        break  # Exit loop if no more pagination prompt
                else:
                    break  # Exit loop if no more data
                
        return output.strip()

    except paramiko.AuthenticationException as auth_exc:
        print(f"Authentication failed for {ip_address}: {str(auth_exc)}")
        return None
    except paramiko.SSHException as ssh_exc:
        print(f"SSH error occurred for {ip_address}: {str(ssh_exc)}")
        return None
    except Exception as e:
        print(f"Error executing command on {ip_address}: {str(e)}")
        return None
    finally:
        ssh_client.close()

def parse_ap_summary(output, device_ip):
    ap_data = []
    lines = output.splitlines()
    header_passed = False
    
    # Define regex pattern to match AP names and flexible AP models
    ap_name_pattern = r"^(\S+)"  # Matches AP names at the beginning of lines
    ap_info_pattern = r"(\S+)\s+\d+\s+(.+)"   # Matches AP information
    ip_pattern = r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # Matches IP addresses
    
    for line in lines:
        if header_passed and line.strip() and not re.search(r"--More--|\(Cisco|#", line):
            # Match AP name
            match_ap_name = re.match(ap_name_pattern, line.strip())
            if match_ap_name:
                ap_name = match_ap_name.group(1).strip()
            else:
                ap_name = None
            
            # Match AP information
            match_ap_info = re.match(ap_info_pattern, line.strip())
            if match_ap_info:
                ap_model = match_ap_info.group(2).strip()
            else:
                ap_model = None
            
            # Match IP address
            match_ip = re.search(ip_pattern, line.strip())
            if match_ip:
                ap_ip = match_ip.group(1).strip()
            else:
                ap_ip = None
            
            # Append AP data as a dictionary, including the device IP address
            ap_data.append({"Device IP": device_ip, "AP Name": ap_name, "AP Model": ap_model, "AP IP": ap_ip})
        
        elif line.startswith('-'):  # Indicates the header has passed
            header_passed = True
    
    return ap_data

if __name__ == "__main__":
    username = 'test' # Your SSH Username
    password = 'password' # Your SSH Password
    ip_addresses = ['192.168.1.1', '192.168.1.2']  # Replace with actual IP addresses

    commands = [
        'show ap summary',
        'no',
        username,
        password,
        'terminal length 0',  # Disable pagination
        'show ap summary'
    ]
    
    # Initialize an empty list to collect AP data
    ap_data = []
    
    try:
        for ip_address in ip_addresses:
            print(f"Connecting to {ip_address}...")
            output = execute_ssh_command(ip_address, username, password, commands)
            if output:
                print(f"Raw output from {ip_address}:")
                print(output)  # Print the raw output to verify it's being captured
                parsed_output = parse_ap_summary(output, ip_address)
                print(f"Parsed output from {ip_address}:")
                print(parsed_output)  # Print the parsed output to verify correct parsing
                ap_data.extend(parsed_output)
    
    except paramiko.AuthenticationException as auth_exc:
        print(f"Authentication failed: {str(auth_exc)}")
    except paramiko.SSHException as ssh_exc:
        print(f"SSH error occurred: {str(ssh_exc)}")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Create a DataFrame from the collected AP data
        df = pd.DataFrame(ap_data, columns=['Device IP', 'AP Name','AP Model','AP IP'])
        print('Execution completed.')


df['Model']=df['AP Model'].str.split().str[0]
APInfo=df[['AP Name','Model','AP IP','Device IP']]
APInfo = APInfo[~APInfo['Model'].isna()]
APInfo.drop_duplicates(subset=['AP Name','AP IP'])
ainfo16=APInfo
ainfo16=WLCs.merge(ainfo16,how='left',left_on='managementIpAddress',right_on='Device IP')
APSInformation=ainfo16[['hostname','managementIpAddress','AP Name','Model','AP IP']]
APSInformation.fillna('No Access Points to Show')
APSInformation.drop_duplicates(subset=['managementIpAddress','AP IP'],inplace=True)
print("Last Information of Access Points")
APSInformation