from flask import Blueprint, jsonify
from services.email_service import EmailService
from config import Config

email_bp = Blueprint('email_bp', __name__)

@email_bp.route('/fetch-emails', methods=['GET'])
def fetch_emails():
    email_service = EmailService(Config.GMAIL_USERNAME, Config.GMAIL_PASSWORD)
    emails = email_service.fetch_emails()
    emails_data = [{
        'sender': email.sender,
        'subject': email.subject,
        'date': email.date,
        'attachments': email.attachments
    } for email in emails]
    return jsonify(emails_data)
