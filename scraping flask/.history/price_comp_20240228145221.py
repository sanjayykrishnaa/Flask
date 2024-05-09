from flask import Flask, jsonify
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
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

    prices = {}
    for site, competitor_data in competitor.items():
        items = fetch_data(category, search_term, site)
        if isinstance(items, list):
            prices[site] = [item['Price'] for item in items]

    # Check if all arrays have the same length
    lengths = set(len(prices[site]) for site in prices)
    if len(lengths) > 1:
        # Arrays have different lengths, save the data but handle plotting differently
        df = pd.DataFrame({k: pd.Series(v) for k, v in prices.items()})
        # Get the current directory of the script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Save the Excel file in the same directory as the script
        excel_file_path = os.path.join(current_dir, 'prices_comparison.xlsx')
        df.to_excel(excel_file_path, index=False)
        return jsonify({"message": "Arrays have different lengths, but data saved for comparison"})

    # Arrays have the same length, proceed with plotting
    df = pd.DataFrame(prices)
    plt.figure(figsize=(10, 6))
    for site, prices in prices.items():
        plt.plot(prices, label=site)
    plt.title(f'Price comparison for {category}: {search_term}')
    plt.xlabel('Item Index')
    plt.ylabel('Price')
    plt.legend()
    # Get the current directory of the script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Save the plot image in the same directory as the script
    image_file_path = os.path.join(current_dir, 'price_comparison.png')
    plt.savefig(image_file_path)

    return jsonify({"message": "Prices compared and saved to price_comparison.png"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
