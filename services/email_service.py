import os
from imaplib import IMAP4_SSL, IMAP4
from email import message_from_bytes
from datetime import datetime
from models.email_model import Email
from utils.email_utils import download_attachments
from utils.json_utils import process_json_file

class EmailService:
    def __init__(self, username, password):
        try:
            self.mail = IMAP4_SSL('imap.gmail.com')
            self.mail.login(username, password)
            status, response = self.mail.select('inbox')
            if status != 'OK':
                raise IMAP4.error(f"Failed to select inbox: {status}")
        except IMAP4.error as e:
            print(f"Error during connection or authentication: {e}")
            raise

    def fetch_emails(self):
        try:
            if self.mail.state != 'SELECTED':
                status, response = self.mail.select('inbox')
                if status != 'OK':
                    raise IMAP4.error(f"Failed to reselect inbox: {status}")

            today_date = datetime.now().strftime('%d-%b-%Y')
            status, messages = self.mail.search(None, f'(UNSEEN SINCE {today_date})')
            if status != 'OK':
                raise IMAP4.error(f"Failed to search emails: {status}")

            email_ids = messages[0].split()
            emails = []

            for email_id in email_ids:
                res, msg = self.mail.fetch(email_id, '(RFC822)')
                for response_part in msg:
                    if isinstance(response_part, tuple):
                        msg = message_from_bytes(response_part[1])
                        if self._is_valid_email(msg):
                            email_date = msg['date']
                            try:
                                email_date_obj = datetime.strptime(email_date, '%a, %d %b %Y %H:%M:%S %z')
                            except ValueError:
                                continue 

                            email_date_str = email_date_obj.strftime('%d-%b-%Y')

                            if email_date_str != today_date:
                                continue  

                            codigo_generacion = None
                            attachments = []

                            # Download and Process JSON attachment
                            for part in msg.walk():
                                if part.get_content_maintype() == 'multipart':
                                    continue
                                if part.get_content_type() == 'application/json':
                                    json_files = download_attachments(part)
                                    for attachment in json_files:
                                        if attachment.endswith('.json'):
                                            codigo_generacion = process_json_file(attachment)
                                            attachments.append(attachment)
                                            if codigo_generacion is None:
                                                # Delete attachments JSON if not validate
                                                for file in attachments:
                                                    if os.path.exists(file):
                                                        try:
                                                            os.remove(file)
                                                            print(f"Archivo {file} eliminado por falta de nodos requeridos")
                                                        except Exception as e:
                                                            print(f"Error deleting file {file}: {e}")
                                                attachments = []
                                                break
                                    if codigo_generacion:
                                        break  # If a valid JSON was already found, search no further

                            # Download PDF only if the JSON is valid
                            if codigo_generacion:
                                pdf_downloaded = False
                                for part in msg.walk():
                                    if part.get_content_maintype() == 'multipart':
                                        continue
                                    if part.get_content_type() == 'application/pdf':
                                        if not pdf_downloaded:
                                            pdf_files = download_attachments(part)
                                            for attachment in pdf_files:
                                                # Rename the PDF with the codigo_generacion
                                                pdf_new_file_path = os.path.join(os.path.dirname(attachment), f"{codigo_generacion}.pdf")
                                                os.rename(attachment, pdf_new_file_path)
                                                attachments.append(pdf_new_file_path)
                                                pdf_downloaded = True
                                                break  

                            if codigo_generacion:
                                email = Email(
                                    sender=msg['from'],
                                    subject=msg['subject'],
                                    date=msg['date'],
                                    attachments=attachments
                                )
                                emails.append(email)
                                self.mail.store(email_id, '+FLAGS', '\\Seen')
                            else:
                                # Mark as unread if the JSON is invalid
                                self.mail.store(email_id, '-FLAGS', '\\Seen')
                        else:
                           # Mark as unread if invalid
                            self.mail.store(email_id, '-FLAGS', '\\Seen')
            return emails
        except IMAP4.error as e:
            print(f"IMAP error occurred: {e}")
            return []

    def _is_valid_email(self, msg):
        has_json = False
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get_content_type() == 'application/json':
                has_json = True
        return has_json