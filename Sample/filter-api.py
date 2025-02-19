import requests

# Base API Endpoint
AZURE_PRICING_URL = "https://prices.azure.com/api/retail/prices"

def fetch_all_vm_prices(region):
    """Fetch all VM prices for a given region from Azure Retail API."""
    api_url = f"{AZURE_PRICING_URL}?$filter=serviceName eq 'Virtual Machines' and armRegionName eq '{region}' and currencyCode eq 'USD'"
    
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
            print(f"Error fetching data: {e}")
            break  # Stop on error

    return all_data

def list_available_series(vm_data):
    """Extracts and lists unique VM Series from the fetched data."""
    series_set = {vm["productName"].split(" ")[2] for vm in vm_data if len(vm["productName"].split(" ")) > 2}
    
    print("\n===== Available VM Series =====")
    for series in sorted(series_set):
        print(f"- {series}")
    
    print(f"\nTotal VM Series found: {len(series_set)}")
    return sorted(series_set)

def list_available_skus(vm_data, selected_series):
    """Extracts and lists available SKUs for the selected series."""
    skus = {vm["skuName"] for vm in vm_data if selected_series in vm["productName"]}
    
    print("\n===== Available VM SKUs =====")
    for sku in sorted(skus):
        print(f"- {sku}")
    
    print(f"\nTotal VM SKUs found: {len(skus)}")
    return skus

def calculate_vm_cost(vm_data, selected_sku):
    """Finds the price of the selected VM SKU and calculates the monthly cost."""
    matching_vms = [vm for vm in vm_data if vm["skuName"] == selected_sku]

    if not matching_vms:
        print("Selected SKU not found. Please try again.")
        return 0
    
    # Pick the first valid price entry (could be multiple pricing tiers)
    price_per_hour = matching_vms[0].get("retailPrice", 0)
    return float(price_per_hour) * 730  # Convert hourly rate to monthly cost

# ===== User Inputs =====
print("\n===== Azure VM Pricing Calculator =====")
region = input("Enter Azure region (e.g., eastus, westus, westeurope): ").strip()

# Fetch all VM pricing data for the region
vm_data = fetch_all_vm_prices(region)

if not vm_data:
    print("No data found for the given region. Please try again.")
else:
    # List available VM series
    available_series = list_available_series(vm_data)
    selected_series = input("\nEnter VM Series from the list above: ").strip()

    # List available SKUs for the selected series
    available_skus = list_available_skus(vm_data, selected_series)
    selected_sku = input("\nEnter SKU from the list above: ").strip()

    # Calculate cost
    vm_cost = calculate_vm_cost(vm_data, selected_sku)

    # Display results
    print("\n===== Estimated Monthly Cost =====")
    print(f"Region       : {region}")
    print(f"VM Series    : {selected_series}")
    print(f"Selected SKU : {selected_sku}")
    print(f"Total Cost   : ${vm_cost:.2f}")
    print("===================================")
