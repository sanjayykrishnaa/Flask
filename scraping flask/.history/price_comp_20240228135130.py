from flask import Flask, jsonify
import json
import requests
import pandas as pd
import os

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
            for category_dict in categories:
                if category.lower() in category_dict['name'].lower() and search_term.lower() in item['name'].lower():
                    found_items.append({
                        "Store": site,
                        "Product Name": item['name'],
                        "Category": category_dict['name'],
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

    # Create a list to store all data
    all_data = []
    for site, items in data.items():
        if site == 'sanday mart':
            # Include product name, category, and price under the store name "sanday mart"
            for item in items:
                all_data.append({
                    "Store": site,
                    "Product Name": item.get('Product Name', ''),
                    "Category": item.get('Category', ''),
                    "Price": item['Price']
                })
        else:
            # Only include price under other store names
            for item in items:
                all_data.append({
                    "Store": site,
                    "Price": item['Price']
                })

    df = pd.DataFrame(all_data)
    excel_file_path = 'prices_comparison.xlsx'
    df.to_excel(excel_file_path)

    return jsonify({"message": f"Prices compared and saved to {excel_file_path}"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
