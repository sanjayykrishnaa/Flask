from flask import Flask
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

def fetch_data(category, search_term, site):
    with open('configs/competitor.json', 'r') as file:
        competitors = json.load(file)
    
    data = []
    for competitor in competitors:
        if site == competitor['name']:
            url = f"{competitor['store']}{search_term}"
            headers = {
                'Accept-Language': "en-US,en;q=0.9,hi;q=0.8",
                'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
                'Cookie': competitor['cookie']
            }
            response = requests.get(url, headers=headers)
            items = response.json().get('items', [])
            for item in items:
                categories = item.get('categories', [])
                for category_dict in categories:
                    if category in category_dict['name'].lower():
                        if search_term in item['name'].lower():
                            data.append({
                                "name": item['name'],
                                "price": item['base_price'],
                                "site": competitor['name']
                            })
    return data

@app.route('/api/v1/getitem/<site>/<category>/<search_term>')   
def getitem(category, search_term, site):
    data = fetch_data(category, search_term, site)
    if data:
        df = pd.DataFrame(data)
        # Save data to .xlsx file
        df.to_excel('items_data.xlsx', index=False)
        
        # Compare prices and visualize using Matplotlib
        plt.figure(figsize=(10, 6))
        for site, group in df.groupby('site'):
            plt.plot(group['name'], group['price'], label=site)
        plt.xlabel('Product')
        plt.ylabel('Price')
        plt.title('Comparison of Prices')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig('price_comparison.png')
        plt.close()
        
        return {"status": 200, "message": "Data fetched successfully and saved."}
    else:
        return {"status": 404, "message": "No data found."}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
