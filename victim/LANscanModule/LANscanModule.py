import socket
import ipaddress
import psutil
import urllib.request
import nmap
from scapy.all import IP, TCP, ICMP, srp1, Ether, sr1, srp, ARP, rdpcap, sniff 

class LAN_discovery:

    def __init__(self):
        self.hostname = self.get_hostname()
        self.ip = self.get_host_ip()
        self.netmask = self.get_netmask()
        self.subnet = str(self.get_subnet())
        self.public_ip_address = self.get_public_ip()
        self.hosts = []
         

    # GET HOSTNAME
    def get_hostname(self):
        return socket.gethostname()

    # GET HOST IP
    def get_host_ip(self):
        return socket.gethostbyname(self.hostname)
    
    # CALCULATE SUBNET MASK
    def get_netmask(self):
        # Use psutil to fetch the subnet mask and calculate CIDR
        interfaces = psutil.net_if_addrs()
        for interface, addresses in interfaces.items():
            for addr in addresses:
                if addr.family == socket.AF_INET and addr.address == self.ip:
                    netmask = addr.netmask
                    return netmask
        return None
    
    def get_subnet(self):
        return ipaddress.ip_network(f'{self.ip}/{self.netmask}', strict=False)
    
    # PUBLIC IP 
    def get_public_ip(self):
        try:
            return urllib.request.urlopen('https://v4.ident.me/').read().decode('utf8')
        except Exception as error:
            print(f"failed: {error}")
            return None

    # HOST DISCOVERY
    def scan_network(self):
        """
        a function which scans the subnet for active hosts by sending an arp broadcast frame

        args:
        ip_range str: a string representing the subnet you wish to scan eg. 192.168.1.0/24

        returns: a dictionary of online hosts, containing their mac address and ip address
        """
        print("[INFO] starting host discovery...")
        arp_request = ARP(pdst=self.subnet) # create a arp request
        ether_frame = Ether(dst="ff:ff:ff:ff:ff:ff") # create a broadcast frame
        packet = ether_frame / arp_request
        result = srp(packet, timeout=2, verbose=False)[0] 
  

        for sent, recieved in result:
            self.hosts.append({"IP": recieved.psrc, "MAC": recieved.hwsrc})
        
        print(f"[+] hosts found: {self.hosts}")

    # PORT SCAN DEVICES
    def port_scan(self):
        """
        a method which preforms an nmap scan 
        """
        print("[+] starting port scan...")
        for host in self.hosts:


            scanner = nmap.PortScanner()
            target = host["IP"]
            
            
            try:
                # Perform the scan with a timeout of 10 seconds
                scanner.scan(target, '22-443', arguments='--host-timeout 10s')
                open_ports = []
                if 'tcp' in scanner[target]:
                    for port, port_data in scanner[target]['tcp'].items():
                        if port_data['state'] == 'open':
                            open_ports.append({
                                'port': port,
                                'service': port_data.get('name', 'Unknown')
                            })
                
                host["vendor"] = scanner[target].get('vendor', 'Unknown')
                host["open_ports"] = open_ports

            except Exception as e:
                print(f"Error scanning {target}: {e}")


    def results(self):
        """
        a method which puts all the found data into a dictionary for exfiltration
        """
        return {
            "hostname": self.hostname,
            "ip_address": self.ip,
            "public_ip_address":self.public_ip_address,
            "local_network_scan": self.hosts
        }

def automate():
    lan_discovery = LAN_discovery()
    lan_discovery.scan_network()
    lan_discovery.port_scan()

    return lan_discovery.results()


if __name__ == "__main__":

    lan_discovery = LAN_discovery()
    print(lan_discovery.ip)
    print(lan_discovery.netmask)
    lan_discovery.scan_network()
    lan_discovery.port_scan()