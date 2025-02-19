import requests
from flask import Flask, jsonify

API_URL = "https://prices.azure.com/api/retail/prices?$filter=serviceName eq 'Virtual Machines' and armRegionName eq 'eastus' and contains(productName, 'Windows') and currencyCode eq 'USD'"

app = Flask(__name__)

# Function to fetch all pages from the API and merge data
def fetch_all_pages(api_url):
    all_data = []
    next_page_url = api_url

    while next_page_url:
        print(f"Fetching data from: {next_page_url}")  # Debug: Show the current page URL
        try:
            response = requests.get(next_page_url, timeout=10)
            response.raise_for_status()  # Raise an error for any bad HTTP responses
            data = response.json()
            
            if "Items" in data:
                all_data.extend(data["Items"])
            else:
                print(f"No 'Items' found in response, data: {data}")  # Debug: Check the structure of response
            
            next_page_url = data.get("NextPageLink")  # Get the next page URL if available
            print(f"Next page URL: {next_page_url}")  # Debug: Show the next page URL
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")  # Debug: Print any errors during request

    return all_data

# Route to fetch and return the merged results as a JSON response
@app.route('/azure-pricing', methods=['GET'])
def get_azure_pricing():
    all_vm_prices = fetch_all_pages(API_URL)
    return jsonify({"total_records": len(all_vm_prices), "data": all_vm_prices})

if __name__ == '__main__':
    app.run(debug=True)
