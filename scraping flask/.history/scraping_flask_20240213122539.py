from flask import Flask
import requests
import json

app = Flask(__name__)


@app.route('/')
def Home():
    return 'Home Page'


@app.route('/api/v1/getsprouts/<category>/<fruit>')
def getsprouts(category, fruit):
    with open('competitor.json', 'r') as file:
        competitor = json.load(file)['sprouts']

    URL = f"{competitor['store_api']}{category}/{fruit}"
    HEADERS = {
        'Accept-Language': "en-US,en;q=0.9,hi;q=0.8",
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
        'Cookie': competitor['cookie']
    }
    response = requests.get(URL, headers=HEADERS)
    data = response.json()
    return data['items'][0]['name']


if __name__ == "__main__":
    app.run(debug=True)
