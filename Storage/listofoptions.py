import requests
import time
from collections import defaultdict

# Function to fetch data with better error handling and pagination
def get_azure_pricing(filter_expression):
    url = "https://prices.azure.com/api/retail/prices"
    params = {
        "$filter": filter_expression,
        "$top": 100
    }
    all_items = []

    while True:
        print(f"\nFetching data from: {url}")
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching data from Azure Retail API. Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        data = response.json()
        items = data.get("Items", [])
        all_items.extend(items)
        
        # Check if there's a next page
        next_link = data.get("NextPageLink", None)
        if not next_link:
            break
        
        url = next_link
        time.sleep(0.5)  # To avoid rate limiting

    return all_items

# User Input for Region
region = input("Enter region (e.g., eastus): ").strip()

# Define focused filters
filters = {
    "Data Stored": f"serviceName eq 'Storage' and armRegionName eq '{region}' and contains(meterName, 'Data Stored')",
    "Write Operations": f"serviceName eq 'Storage' and armRegionName eq '{region}' and contains(meterName, 'Write Operations')",
    "Read Operations": f"serviceName eq 'Storage' and armRegionName eq '{region}' and contains(meterName, 'Read Operations')",
    "List Operations": f"serviceName eq 'Storage' and armRegionName eq '{region}' and contains(meterName, 'List')",
    "Data Transfer": f"serviceName eq 'Bandwidth' and armRegionName eq '{region}' and contains(meterName, 'Data Transfer Out')"
}

# Fetch Data for Each Category
pricing_data = defaultdict(list)
for category, filter_expression in filters.items():
    print(f"\nFetching prices for: {category}")
    data = get_azure_pricing(filter_expression)
    
    if not data:
        print(f"No data found for {category}. Continuing to next category.")
        continue
    
    pricing_data[category] = data

# Check if any data is fetched
if not pricing_data:
    print("No pricing data found for any category. Please check the region or try again later.")
    exit()

# Organize and Display Options
print("\n===== Available Storage Options =====")
option_map = []
option_counter = 1

for category, items in pricing_data.items():
    print(f"\n-- {category} --")
    for item in items:
        product_name = item.get("productName", "Unknown")
        sku_name = item.get("skuName", "Unknown")
        meter_name = item.get("meterName", "Unknown")
        unit_price = item.get("unitPrice", 0)
        
        print(f"{option_counter}. {product_name} - {sku_name} - {meter_name} - ${unit_price:.5f}/unit")
        option_map.append(item)
        option_counter += 1

print("\n=====================================")

# User Selection for Calculation
selection = int(input("\nSelect an option to calculate price (number): "))
selected_item = option_map[selection - 1]

# Get Required Inputs for Calculation
print("\n===== Enter Values for Calculation =====")
unit_of_measure = selected_item.get("unitOfMeasure", "unit")
quantity = float(input(f"Enter quantity for {unit_of_measure}: "))

# Calculate and Display Cost
unit_price = selected_item.get("unitPrice", 0)
total_cost = quantity * unit_price

print("\n===== Cost Calculation =====")
print(f"Selected Option : {selected_item.get('meterName', 'Unknown')}")
print(f"Unit Price      : ${unit_price:.5f} per {unit_of_measure}")
print(f"Quantity        : {quantity}")
print(f"Total Cost      : ${total_cost:.5f}")
print("=======================================")
