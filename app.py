from flask import Flask
from routes.email_routes import email_bp


app = Flask(__name__)
app.register_blueprint(email_bp, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)

