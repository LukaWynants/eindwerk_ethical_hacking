from Encryption import *


def generate_attacker_keys():
    encryption_attacker = Encryption("", "public_attacker.pem","private_attacker.pem")

    # Generate key pairs
    encryption_attacker.generate_keys()

generate_attacker_keys()
