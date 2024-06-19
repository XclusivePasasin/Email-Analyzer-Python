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
            # Asegúrate de que la carpeta está seleccionada antes de buscar
            if self.mail.state != 'SELECTED':
                status, response = self.mail.select('inbox')
                if status != 'OK':
                    raise IMAP4.error(f"Failed to reselect inbox: {status}")

            # Obtener la fecha actual en el formato necesario para comparación
            today_date = datetime.now().strftime('%d-%b-%Y')

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
                            # Obtener la fecha del correo electrónico
                            email_date = msg['date']
                            email_date_obj = datetime.strptime(email_date, '%a, %d %b %Y %H:%M:%S %z')
                            email_date_str = email_date_obj.strftime('%d-%b-%Y')

                            # Comparar con la fecha actual
                            if email_date_str != today_date:
                                continue  # Saltar este correo si no es del día actual

                            json_valid = False
                            attachments = []

                            # Descargar y procesar archivos JSON
                            for part in msg.walk():
                                if part.get_content_maintype() == 'multipart':
                                    continue
                                if part.get_content_type() == 'application/json':
                                    json_files = download_attachments(part)
                                    for attachment in json_files:
                                        if attachment.endswith('.json'):
                                            json_valid = process_json_file(attachment)
                                            attachments.append(attachment)
                                            if not json_valid:
                                                # Eliminar archivos adjuntos si el JSON no es válido
                                                for file in attachments:
                                                    try:
                                                        os.remove(file)
                                                    except Exception as e:
                                                        print(f"Error deleting file {file}: {e}")
                                                attachments = []
                                                break  # Salir del bucle si el JSON no es válido
                                    if json_valid:
                                        break  # Si ya se encontró un JSON válido, no buscar más

                            # Descargar PDF solo si el JSON es válido
                            if json_valid:
                                pdf_downloaded = False
                                for part in msg.walk():
                                    if part.get_content_maintype() == 'multipart':
                                        continue
                                    if part.get_content_type() == 'application/pdf':
                                        if not pdf_downloaded:
                                            pdf_files = download_attachments(part)
                                            for attachment in pdf_files:
                                                attachments.append(attachment)
                                                pdf_downloaded = True
                                                break  # Solo procesar un archivo PDF

                            if json_valid:
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
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get_content_type() == 'application/json':
                has_json = True
        return has_json