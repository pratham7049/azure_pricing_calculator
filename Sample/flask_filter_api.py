from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Base API Endpoint
AZURE_PRICING_URL = "https://prices.azure.com/api/retail/prices"

def fetch_all_vm_prices(region, currency='USD', meter_name=None, product_name=None, sku_name=None):
    """Fetch all VM prices for a given region from Azure Retail API with additional filters."""
    filters = [
        "serviceName eq 'Virtual Machines'",
        f"armRegionName eq '{region}'",
        f"currencyCode eq '{currency}'"
    ]
    if meter_name:
        filters.append(f"meterName eq '{meter_name}'")
    if product_name:
        filters.append(f"productName eq '{product_name}'")
    if sku_name:
        filters.append(f"skuName eq '{sku_name}'")
    
    api_url = f"{AZURE_PRICING_URL}?$filter={' and '.join(filters)}"
    
    all_data = []
    next_page_url = api_url
    
    while next_page_url:
        try:
            response = requests.get(next_page_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "Items" in data:
                all_data.extend(data["Items"])
            
            next_page_url = data.get("NextPageLink")  # Handle pagination
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    return all_data

@app.route('/vm-prices', methods=['GET'])
def get_vm_prices():
    region = request.args.get('region')
    currency = request.args.get('currency', 'USD')
    meter_name = request.args.get('meter_name')
    product_name = request.args.get('product_name')
    sku_name = request.args.get('sku_name')
    
    if not region:
        return jsonify({"error": "Missing 'region' parameter"}), 400
    
    vm_data = fetch_all_vm_prices(region, currency, meter_name, product_name, sku_name)
    return jsonify(vm_data)

@app.route('/vm-series', methods=['GET'])
def get_vm_series():
    region = request.args.get('region')
    if not region:
        return jsonify({"error": "Missing 'region' parameter"}), 400
    
    vm_data = fetch_all_vm_prices(region)
    if "error" in vm_data:
        return jsonify(vm_data), 500
    
    series_set = {vm["productName"].split(" ")[2] for vm in vm_data if len(vm["productName"].split(" ")) > 2}
    return jsonify(sorted(series_set))

@app.route('/vm-skus', methods=['GET'])
def get_vm_skus():
    region = request.args.get('region')
    series = request.args.get('series')
    
    if not region or not series:
        return jsonify({"error": "Missing 'region' or 'series' parameter"}), 400
    
    vm_data = fetch_all_vm_prices(region)
    if "error" in vm_data:
        return jsonify(vm_data), 500
    
    skus = {vm["skuName"] for vm in vm_data if series in vm["productName"]}
    return jsonify(sorted(skus))

@app.route('/vm-cost', methods=['GET'])
def get_vm_cost():
    region = request.args.get('region')
    sku = request.args.get('sku')
    
    if not region or not sku:
        return jsonify({"error": "Missing 'region' or 'sku' parameter"}), 400
    
    vm_data = fetch_all_vm_prices(region, sku_name=sku)
    if "error" in vm_data:
        return jsonify(vm_data), 500
    
    matching_vms = [vm for vm in vm_data if vm["skuName"] == sku]
    if not matching_vms:
        return jsonify({"error": "SKU not found"}), 404
    
    price_per_hour = matching_vms[0].get("retailPrice", 0)
    total_cost = float(price_per_hour) * 730  # Convert hourly rate to monthly cost
    
    return jsonify({
        "region": region,
        "sku": sku,
        "hourly_price": price_per_hour,
        "monthly_cost": round(total_cost, 2)
    })

if __name__ == '__main__':
    app.run(debug=True)
