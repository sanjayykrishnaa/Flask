from flask import Flask
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

def item_parser(category, search_term, site):
    with open('configs/competitor.json', 'r') as file:
        competitor = json.load(file)[site]
        
    URL = f"{competitor['store_api']}{category}/{search_term}"
    HEADERS = { 
        'Accept-Language': "en-US,en;q=0.9,hi;q=0.8",
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
        'Cookie': competitor['cookie']
    }
    response = requests.get(URL, headers=HEADERS)
    data = response.json()
    
    prices = []
    if 'items' in data:
        items = data['items']
        for item in items:
            categories = item.get('categories', [])
            for category_dict in categories:
                if category in category_dict.get('name', '').lower():
                    if search_term in item.get('name', '').lower():
                        price = item.get('base_price')
                        if price:
                            prices.append(price)
                        break
    return prices

@app.route('/api/v1/getitem/<site>/<category>/<search_term>')   
def getitem(category, search_term, site):
    return json.dumps(item_parser(category, search_term, site))

@app.route('/api/v1/compare_prices/<category>/<search_term>')
def compare_prices(category, search_term):
    sites = ['sprouts', 'tfm', 'wegmans']
    data = {}
    for site in sites:
        data[site] = item_parser(category, search_term, site)
    
    df = pd.DataFrame(data)
    df.to_excel('prices_comparison.xlsx', index=False)
    
    # Visualize price differences
    plt.figure(figsize=(10, 6))
    df.boxplot()
    plt.title('Price Comparison')
    plt.xlabel('Website')
    plt.ylabel('Price')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('price_comparison_plot.png')
    
    return 'Price comparison data saved to prices_comparison.xlsx and plot saved to price_comparison_plot.png'

if __name__ == '__main__':
    app.run(debug=True, port=5000)
