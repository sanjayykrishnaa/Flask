from flask import Flask
import requests
import json

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'Flask
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)