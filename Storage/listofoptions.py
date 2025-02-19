import requests

BASE_URL = "https://prices.azure.com/api/retail/prices"

def fetch_data(filter_query):
    url = f"{BASE_URL}?$filter={filter_query}"
    print(f"\nFetching data with filter: {filter_query}")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("Items", [])
    else:
        print(f"Error fetching data. Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def list_regions():
    filter_query = "serviceFamily eq 'Storage'"
    data = fetch_data(filter_query)
    if data:
        regions = sorted(set(item["armRegionName"] for item in data if "armRegionName" in item))
        return regions
    else:
        print("No data found. Please check the filters or try again later.")
        return []

def list_storage_types(region):
    filter_query = f"serviceFamily eq 'Storage' and armRegionName eq '{region}'"
    data = fetch_data(filter_query)
    if data:
        storage_types = sorted(set(item["productName"] for item in data if "productName" in item))
        return storage_types
    else:
        print("No data found. Please check the filters or try again later.")
        return []

def list_storage_tiers(region, storage_type):
    filter_query = f"serviceFamily eq 'Storage' and armRegionName eq '{region}' and productName eq '{storage_type}'"
    data = fetch_data(filter_query)
    if data:
        storage_tiers = sorted(set(item["skuName"] for item in data if "skuName" in item))
        return storage_tiers
    else:
        print("No data found. Please check the filters or try again later.")
        return []

def get_pricing(region, storage_type, storage_tier):
    filter_query = f"serviceFamily eq 'Storage' and armRegionName eq '{region}' and productName eq '{storage_type}' and skuName eq '{storage_tier}'"
    data = fetch_data(filter_query)
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

if __name__ == "__main__":
    print("\n===== Fetching Available Azure Regions =====")
    regions = list_regions()
    if not regions:
        exit()
    
    print("\nAvailable Azure Regions:")
    for i, region in enumerate(regions):
        print(f"{i+1}. {region}")
    
    region_choice = int(input("\nSelect a region by number: ")) - 1
    selected_region = regions[region_choice]
    
    print(f"\n===== Fetching Storage Types for Region: {selected_region} =====")
    storage_types = list_storage_types(selected_region)
    if not storage_types:
        exit()
    
    print("\nAvailable Storage Types:")
    for i, storage_type in enumerate(storage_types):
        print(f"{i+1}. {storage_type}")
    
    storage_type_choice = int(input("\nSelect a storage type by number: ")) - 1
    selected_storage_type = storage_types[storage_type_choice]

    print(f"\n===== Fetching Storage Tiers for {selected_storage_type} in {selected_region} =====")
    storage_tiers = list_storage_tiers(selected_region, selected_storage_type)
    if not storage_tiers:
        exit()

    print("\nAvailable Storage Tiers:")
    for i, storage_tier in enumerate(storage_tiers):
        print(f"{i+1}. {storage_tier}")
    
    storage_tier_choice = int(input("\nSelect a storage tier by number: ")) - 1
    selected_storage_tier = storage_tiers[storage_tier_choice]

    print(f"\n===== Fetching Pricing for {selected_storage_type} - {selected_storage_tier} in {selected_region} =====")
    get_pricing(selected_region, selected_storage_type, selected_storage_tier)
