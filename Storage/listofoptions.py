import requests

BASE_URL = "https://prices.azure.com/api/retail/prices"
SERVICE_FAMILY = "Storage"

def fetch_data(filter_query):
    url = f"{BASE_URL}?$filter={filter_query}"
    print(f"\nFetching data with filter: {filter_query}")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("Items", [])
    else:
        print(f"Error fetching data. Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return []

def get_unique_values(data, key):
    return sorted(set(item[key] for item in data if key in item))

def list_regions():
    data = fetch_data(f"serviceFamily eq '{SERVICE_FAMILY}'")
    return get_unique_values(data, "armRegionName")

def list_storage_types(region):
    data = fetch_data(f"serviceFamily eq '{SERVICE_FAMILY}' and armRegionName eq '{region}'")
    return get_unique_values(data, "productName")

def list_storage_tiers(region, storage_type):
    data = fetch_data(f"serviceFamily eq '{SERVICE_FAMILY}' and armRegionName eq '{region}' and productName eq '{storage_type}'")
    return get_unique_values(data, "skuName")

def get_pricing(region, storage_type, storage_tier):
    data = fetch_data(f"serviceFamily eq '{SERVICE_FAMILY}' and armRegionName eq '{region}' and productName eq '{storage_type}' and skuName eq '{storage_tier}'")
    if data:
        print("\n===== Pricing Details =====")
        for item in data:
            print(f"\nProduct Name : {item['productName']}")
            print(f"SKU Name     : {item['skuName']}")
            print(f"Meter Name   : {item['meterName']}")
            print(f"Unit Price   : ${item['unitPrice']} per {item['unitOfMeasure']}")
            print(f"Region       : {item['armRegionName']}")
            print(f"Start Date   : {item['effectiveStartDate']}")
    else:
        print("No pricing data found. Please check the filters or try again later.")

def get_user_selection(options, prompt):
    while True:
        try:
            choice = int(input(prompt)) - 1
            if 0 <= choice < len(options):
                return options[choice]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

if __name__ == "__main__":
    print("\n===== Fetching Available Azure Regions =====")
    regions = list_regions()
    if not regions:
        exit("No regions found. Please check the filters or try again later.")
    
    print("\nAvailable Azure Regions:")
    for i, region in enumerate(regions):
        print(f"{i+1}. {region}")
    
    selected_region = get_user_selection(regions, "\nSelect a region by number: ")
    
    print(f"\n===== Fetching Storage Types for Region: {selected_region} =====")
    storage_types = list_storage_types(selected_region)
    if not storage_types:
        exit("No storage types found. Please check the filters or try again later.")
    
    print("\nAvailable Storage Types:")
    for i, storage_type in enumerate(storage_types):
        print(f"{i+1}. {storage_type}")
    
    selected_storage_type = get_user_selection(storage_types, "\nSelect a storage type by number: ")

    print(f"\n===== Fetching Storage Tiers for {selected_storage_type} in {selected_region} =====")
    storage_tiers = list_storage_tiers(selected_region, selected_storage_type)
    if not storage_tiers:
        exit("No storage tiers found. Please check the filters or try again later.")

    print("\nAvailable Storage Tiers:")
    for i, storage_tier in enumerate(storage_tiers):
        print(f"{i+1}. {storage_tier}")
    
    selected_storage_tier = get_user_selection(storage_tiers, "\nSelect a storage tier by number: ")

    print(f"\n===== Fetching Pricing for {selected_storage_type} - {selected_storage_tier} in {selected_region} =====")
    get_pricing(selected_region, selected_storage_type, selected_storage_tier)