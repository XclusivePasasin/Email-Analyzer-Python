import os

class Config:
    GMAIL_USERNAME = os.getenv('GMAIL_USERNAME')
    GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
    DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER', './downloads')
