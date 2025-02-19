import requests
import json

def fetch_azure_storage_prices(region=None, sku=None, meter_name=None, product_name=None):
    base_url = "https://prices.azure.com/api/retail/prices?api-version=2021-10-01-preview"
    filters = ["serviceFamily eq 'Storage'"]
    
    if region:
        filters.append(f"armRegionName eq '{region}'")
    if sku:
        filters.append(f"skuName eq '{sku}'")
    if meter_name:
        filters.append(f"meterName eq '{meter_name}'")
    if product_name:
        filters.append(f"productName eq '{product_name}'")
    
    filter_query = " and ".join(filters)
    url = f"{base_url}&$filter={filter_query}"
    
    all_prices = []
    
    while url:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            data = response.json()
            
            if "Items" in data:
                all_prices.extend(data["Items"])
            else:
                print("Unexpected data format: Missing 'Items' key")
                break
            
            url = data.get("NextPageLink")  # Fetch next page if available
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return []
    
    return all_prices

def calculate_storage_cost(price_per_unit, quantity):
    return price_per_unit * quantity

def display_storage_prices():
    region = input("Enter Azure region (or press Enter to skip): ").strip()
    sku = input("Enter SKU name (or press Enter to skip): ").strip()
    meter_name = input("Enter Meter Name (or press Enter to skip): ").strip()
    product_name = input("Enter Product Name (or press Enter to skip): ").strip()
    quantity = float(input("Enter the quantity (in GB/month or relevant unit): "))
    
    storage_prices = fetch_azure_storage_prices(
        region if region else None, 
        sku if sku else None, 
        meter_name if meter_name else None, 
        product_name if product_name else None
    )
    
    if not storage_prices:
        print("No storage pricing data found.")
        return
    
    print("\nAzure Storage Pricing:\n")
    for item in storage_prices[:20]:  # Limit to first 20 results for readability
        price_per_unit = item.get("retailPrice", 0)
        total_cost = calculate_storage_cost(price_per_unit, quantity)
        print(json.dumps({
            "currencyCode": item.get("currencyCode", "N/A"),
            "tierMinimumUnits": item.get("tierMinimumUnits", "N/A"),
            "retailPrice": price_per_unit,
            "unitPrice": item.get("unitPrice", "N/A"),
            "armRegionName": item.get("armRegionName", "N/A"),
            "location": item.get("location", "N/A"),
            "effectiveStartDate": item.get("effectiveStartDate", "N/A"),
            "meterId": item.get("meterId", "N/A"),
            "meterName": item.get("meterName", "N/A"),
            "productId": item.get("productId", "N/A"),
            "skuId": item.get("skuId", "N/A"),
            "productName": item.get("productName", "N/A"),
            "skuName": item.get("skuName", "N/A"),
            "serviceName": item.get("serviceName", "N/A"),
            "serviceId": item.get("serviceId", "N/A"),
            "serviceFamily": item.get("serviceFamily", "N/A"),
            "unitOfMeasure": item.get("unitOfMeasure", "N/A"),
            "type": item.get("type", "N/A"),
            "isPrimaryMeterRegion": item.get("isPrimaryMeterRegion", "N/A"),
            "armSkuName": item.get("armSkuName", "N/A"),
            "totalCost": total_cost
        }, indent=4))
        print("-" * 80)

if __name__ == "__main__":
    display_storage_prices()
