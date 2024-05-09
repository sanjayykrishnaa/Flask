from flask import Flask
import requests
import json

app = Flask(__name__)


@app.route('/')
def Home():
    return 'Home Page'


@app.route('/api/v1/getsprouts/<categories>/<1>/<fruits>')
def getsprouts(item) :
    with open('competitor.json','r') as file :
        competitor = json.loads(file) ['sprouts']
        
    URL = f"{competitor['store_api']}{item}"
    HEADERS = {

        'Accept-Language': "en-US,en;q=0.9,hi;q=0.8",
        'User-Agent' : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
        'Cookie':competitor ['cookie']
        }
    response = requests.get(URL,headers=HEADERS)
    data = response.json()
    return data['items'][0]['name']

app.run(debug=True)