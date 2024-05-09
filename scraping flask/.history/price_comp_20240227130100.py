from flask import Flask, jsonify
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

def fetch_data(category, search_term, site):
    with open('competitors.json', 'r') as file:
        competitors = json.load(file)
    
    competitor = competitors.get(site)
    if not competitor:
        return jsonify({"error": "Competitor not found"}), 404
    
    URL = competitor['store_api'] + search_term
    HEADERS = { 
        'Accept-Language': "en-US,en;q=0.9,hi;q=0.8",
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
        'Cookie': competitor['cookie']
    }
    
    response = requests.get(URL, headers=HEADERS)
    data = response.json()
    
    if data.get('items'):
        items = data.get('items')
        found_items = []
        for item in items:
            categories = item.get('categories', [])
            for category_dict in categories:
                if category.lower() in category_dict['name'].lower() and search_term.lower() in item['name'].lower():
                    found_items.append({
                        "name": item['name'],
                        "price": item['base_price']
                    })
        return found_items
    else:
        return jsonify({"error": "No items found"}), 404

@app.route('/api/v1/getitem/<site>/<category>/<search_term>')
def getitem(site, category, search_term):
    items = fetch_data(category, search_term, site)
    if isinstance(items, list):
        return jsonify({"items": items})
    else:
        return items

@app.route('/api/v1/compare_prices/<category>/<search_term>')
def compare_prices(category, search_term):
    with open('competitors.json', 'r') as file:
        competitors = json.load(file)

    prices = {}
    for site, competitor in competitors.items():
        items = fetch_data(category, search_term, site)
        if isinstance(items, list):
            prices[site] = [item['price'] for item in items]

    df = pd.DataFrame(prices)
    df.to_excel('prices_comparison.xlsx', index=False)

    plt.figure(figsize=(10, 6))
    for site, prices in prices.items():
        plt.plot(prices, label=site)
    plt.title(f'Price comparison for {category}: {search_term}')
    plt.xlabel('Item Index')
    plt.ylabel('Price')
    plt.legend()
    plt.savefig('price_comparison.png')

    return jsonify({"message": "Prices compared and saved to prices_comparison.xlsx and price_comparison.png"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
