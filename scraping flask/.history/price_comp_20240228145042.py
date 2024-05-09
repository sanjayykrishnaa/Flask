from flask import Flask, jsonify
import json
import requests
import pandas as pd

app = Flask(__name__)

def fetch_data(category, search_term, site):
    with open('configs/competitor.json', 'r') as file:
        competitor = json.load(file)
    
    competitor = competitor.get(site)
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
            if site == 'sanday mart' and category.lower() in [cat['name'].lower() for cat in categories]:
                found_items.append({
                    "Store": site,
                    "Product Name": item['name'],
                    "Category": category,
                    "Price": item['base_price']
                })
            elif site != 'sanday mart':
                found_items.append({
                    "Store": site,
                    "Price": item['base_price']
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
    with open('configs/competitor.json', 'r') as file:
        competitor = json.load(file)

    data = {}
    for site, competitor_data in competitor.items():
        items = fetch_data(category, search_term, site)
        if isinstance(items, list):
            data[site] = items

    if not data:
        return jsonify({"error": "No items found for comparison"}), 404

    all_data = []
    for site, items in data.items():
        all_data.extend(items)

    df = pd.DataFrame(all_data)
    excel_file_path = 'prices_comparison.xlsx'
    df.to_excel(excel_file_path, index=False)

    return jsonify({"message": f"Prices compared and saved to {excel_file_path}"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
