import requests

def fetch_storage_prices():
    url = "https://prices.azure.com/api/retail/prices?$filter=serviceName eq 'Storage' and armRegionName eq 'eastus' and currencyCode eq 'USD'"
    services = {}

    while url:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            return {}

        data = response.json()
        for item in data.get("Items", []):
            product_name = item.get("productName", "Unknown")
            sku_name = item.get("skuName", "Unknown")
            unit_price = item.get("unitPrice", 0.0)
            unit_of_measure = item.get("unitOfMeasure", "Unknown")

            if unit_of_measure == "1 GB" and unit_price > 0:
                key = f"{product_name} - {sku_name}"  # Combine product and SKU
                services[key] = unit_price

        # Get the next page URL
        url = data.get("NextPageLink", None)

    return services

def calculate_storage_price(service_name, storage_size_gb, services):
    if service_name in services:
        return services[service_name] * storage_size_gb
    else:
        print("Selected service not found.")
        return 0.0

if __name__ == "__main__":
    services = fetch_storage_prices()
    
    if not services:
        print("No storage pricing data found.")
    else:
        print("Available Storage Services:")
        for i, service in enumerate(services.keys(), 1):
            print(f"{i}. {service}")

        choice = int(input("Select a storage type by number: "))
        selected_service = list(services.keys())[choice - 1]

        storage_size_gb = float(input("Enter storage size in GB: "))
        total_price = calculate_storage_price(selected_service, storage_size_gb, services)

        print(f"Total estimated cost for {storage_size_gb} GB of {selected_service}: ${total_price:.2f}")
