from flask import Flask
import requests
import json

app = Flask(__name__)


@app.route('/')
def Home():
    return 'Home Page'


@app.route('/api/v1/getsprouts/<category>/<item>')
def getsprouts(item) :
    with open('competitor.json','r') as file :
        competitor = json.loads(file) ['sprouts']
        
    URL = f"{competitor['store_api']}{item}"
