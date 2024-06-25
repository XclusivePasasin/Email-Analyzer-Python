import os
from imaplib import IMAP4_SSL, IMAP4
from email import message_from_bytes
from datetime import datetime
from models.email_model import Email
from utils.email_utils import download_attachments
from utils.json_utils import process_json_file
from services.bd_service import *  

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
            status, messages = self.mail.search(None, f'(SINCE {today_date})')
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

                            attachments = []
                            json_data = None
                            generation_code = None
                            json_files = []
                            pdf_files = []

                            for part in msg.walk():
                                if part.get_content_maintype() == 'multipart':
                                    continue
                                content_type = part.get_content_type()
                                if content_type == 'application/json':
                                    json_files.extend(download_attachments(part))
                                elif content_type == 'application/pdf':
                                    pdf_files.extend(download_attachments(part))

                            # We process the JSON files first
                            for attachment in json_files:
                                if attachment.upper().endswith('.JSON'):
                                    json_data = process_json_file(attachment)
                                    attachments.append(attachment)
                                    if json_data is None:
                                        # Delete invalid JSON files
                                        for file in attachments:
                                            if os.path.exists(file):
                                                try:
                                                    os.remove(file)
                                                    print(f"File {file} removed due to lack of required nodes")
                                                except Exception as e:
                                                    print(f"Error deleting file {file}: {e}")
                                        attachments = []
                                        break
                                    else:
                                        generation_code = json_data['identificacion']['codigoGeneracion']
                                        # Check if the generation code already exists
                                        if check_generation_code_exists(generation_code):
                                            print(f"Generation code {generation_code} already exists. Deleting JSON file.")
                                            if os.path.exists(attachment):
                                                try:
                                                    os.remove(attachment)
                                                    print(f"File {attachment} removed due to duplicate generation code")
                                                except Exception as e:
                                                    print(f"Error deleting file {attachment}: {e}")
                                            attachments = []
                                            break

                            # We process PDF files
                            if json_data:
                                for attachment in pdf_files:
                                    pdf_new_file_path = os.path.join(os.path.dirname(attachment), f"{generation_code}.pdf")
                                    os.rename(attachment, pdf_new_file_path)
                                    attachments.append(pdf_new_file_path)

                            if generation_code and attachments:
                                email = Email(
                                    sender=msg['from'],
                                    subject=msg['subject'],
                                    date=msg['date'],
                                    attachments=attachments
                                )
                                emails.append(email)
                                self.mail.store(email_id, '+FLAGS', '\\Seen')

                                # Insertar datos en la base de datos
                                json_path = os.path.join(os.path.dirname(attachments[0]), f"{generation_code}.json")
                                pdf_path = os.path.join(os.path.dirname(attachments[-1]), f"{generation_code}.pdf")
                                data_bd = {
                                    'generation_code': json_data['identificacion']['codigoGeneracion'],
                                    'control_number': json_data['identificacion']['numeroControl'],
                                    'receiver_name': json_data['receptor']['nombre'],
                                    'issuer_name': json_data['emisor']['nombre'],
                                    'issuer_nit': json_data['emisor']['nit'],
                                    'issuer_nrc': json_data['emisor']['nrc'],
                                    'date': json_data['identificacion']['fecEmi'],
                                    'json_path': json_path,
                                    'pdf_path': pdf_path
                                }
                                InsertInformation(data_bd)
                            else:
                                # Mark as unread if the JSON is invalid
                                self.mail.store(email_id, '-FLAGS', '\\Seen')
                        else:
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
