import os
from config import Config

def download_attachments(msg):
    attachments = []
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        filename = part.get_filename()
        if filename:
            filepath = os.path.join(Config.DOWNLOAD_FOLDER, filename)
            with open(filepath, 'wb') as f:
                f.write(part.get_payload(decode=True))
            attachments.append(filepath)
    return attachments
