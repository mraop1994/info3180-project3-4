from flask.ext.mail import Message
from app import app
from app.config import BaseConfig
from flask.ext.mail import Mail


mail = Mail(app)
app.config.update(
	DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'enter-your-gmail-address',
    MAIL_PASSWORD = 'enter-your-email-password'
	)
mail = Mail(app)


def send_email(to, subject):
    msg = Message(
        subject,
        recipients=[to],
        html="",
        sender='someone@gmail.com'
        # sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)