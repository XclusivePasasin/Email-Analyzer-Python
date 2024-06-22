from flask import Blueprint, jsonify, render_template
from services.email_service import EmailService
from config import Config
from utils.db_utils import get_all_invoices

email_bp = Blueprint('email_bp', __name__)


@email_bp.route('/invoices')
def show_invoices():
    email_service = EmailService(Config.GMAIL_USERNAME, Config.GMAIL_PASSWORD)
    emails = email_service.fetch_emails()
    invoices = get_all_invoices()
    return render_template('invoices.html', invoices=invoices)
