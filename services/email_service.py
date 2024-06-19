import os
from imaplib import IMAP4_SSL, IMAP4
from email import message_from_bytes
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
            # Asegúrate de que la carpeta está seleccionada antes de buscar
            if self.mail.state != 'SELECTED':
                status, response = self.mail.select('inbox')
                if status != 'OK':
                    raise IMAP4.error(f"Failed to reselect inbox: {status}")
            
            status, messages = self.mail.search(None, 'UNSEEN')
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
                            attachments = download_attachments(msg)
                            
                            # Procesar cada archivo JSON descargado
                            for attachment in attachments:
                                if attachment.endswith('.json'):
                                    process_json_file(attachment)

                            email = Email(
                                sender=msg['from'],
                                subject=msg['subject'],
                                date=msg['date'],
                                attachments=attachments
                            )
                            emails.append(email)
                            self.mail.store(email_id, '+FLAGS', '\\Seen')
            return emails
        except IMAP4.error as e:
            print(f"IMAP error occurred: {e}")
            return []

    def _is_valid_email(self, msg):
        has_json = False
        has_pdf = False
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get_content_type() == 'application/json':
                has_json = True
            if part.get_content_type() == 'application/pdf':
                has_pdf = True
        return has_json and has_pdf
