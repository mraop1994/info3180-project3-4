import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/project3_4'
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://abvsxfjmsnzrmf:xQqm4QltLO3oPktilH-G9a17aC@ec2-54-83-36-90.compute-1.amazonaws.com:5432/dd92jb06bbucik"
db = SQLAlchemy(app)
db.create_all()

# email server
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# administrator list
ADMINS = ['a.philp1994@gmail.com']

from app import views, models