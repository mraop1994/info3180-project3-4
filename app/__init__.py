import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/project3_4'
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://abvsxfjmsnzrmf:xQqm4QltLO3oPktilH-G9a17aC@ec2-54-83-36-90.compute-1.amazonaws.com:5432/dd92jb06bbucik"
db = SQLAlchemy(app)
db.create_all()

from app import views, models