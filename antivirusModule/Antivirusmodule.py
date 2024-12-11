import subprocess

class AntivirusModule:

    def __init__(self):
        self.detected_antivirus = ""

    def detect_antivirus(self):
        """
        a method that scabns for antivirus software on a windows computer
        """
        try:
            powershell_command = 'Get-CimInstance -Namespace "Root\\SecurityCenter2" -ClassName AntivirusProduct | Select-Object displayName, productState'
            result = subprocess.run(['powershell', '-Command', powershell_command], capture_output=True, text=True)
            
            output = result.stdout

            #split output in lines
            lines = output.splitlines()
            #remove uneeded information
            antiviruses = lines[3:-2]

            if antiviruses:
                for antivirus in antiviruses:
                    antivirus_info = antivirus.split() 
                    antivirus_name = " ".join(antivirus_info[:-1])  # All except the last part (product state)
                    self.detected_antivirus = antivirus_name
                    print(f"Detected antivirus: {self.detected_antivirus}")

            else:
                print("[!] No antivirus detected.")

        except:
            print("[!] Couldnt detect antivirus")

if __name__=="__main__":
    antivirusModule = AntivirusModule()

    antivirusModule.detect_antivirus()