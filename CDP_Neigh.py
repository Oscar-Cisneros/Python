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
    OutgoingPorts = re.findall(r"Port ID \(outgoing port\): (.+)",output)
    
    for device_id, platform, interface,ManamentIP,OutgoingPort in zip(device_ids, platforms, interfaces,ManamentIP,OutgoingPorts):
        neighbor = {
            "Neighbor": device_id.strip(),
            "Platform": platform.strip(),
            "Local Interface": interface.strip(),
            "Interface IP": ManamentIP.strip(),
            "Device IP Address": device_ip,
            "Out Going Port":OutgoingPort.strip()
            
            
        }
        neighbors.append(neighbor)
    
    return neighbors

if __name__ == "__main__":
    usernames = ['YourDeviceUsername']
    passwords = ['YourDevicePassword']
    ip_addresses = ['YourListofIPAdresses']

  # List of IP addresses
    
    commands = [
        'terminal length 0',
        'show cdp nei detail',
    ]
    
    # Initialize an empty DataFrame
    df = pd.DataFrame(columns=['Neighbor', 'Platform', 'Local Interface','Out Going Port'])
    
    try:
        for ip_address in ip_addresses:
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
                    df = pd.concat([df, new_row], ignore_index=True)
    
    except paramiko.AuthenticationException as auth_exc:
        print(f"Authentication failed: {str(auth_exc)}")
    except paramiko.SSHException as ssh_exc:
        print(f"SSH error occurred: {str(ssh_exc)}")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        print('Execution completed.')