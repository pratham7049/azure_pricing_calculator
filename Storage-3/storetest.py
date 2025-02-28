import requests
import json

# Azure Pricing API for Storage
STORAGE_URL = "https://azure.microsoft.com/api/v3/pricing/storage/calculator/?culture=en-in&discount=mca"

def fetch_storage_pricing():
    """Fetch Azure Storage pricing from API."""
    response = requests.get(STORAGE_URL, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            print("Failed to parse JSON response.")
            return None
    else:
        print(f"Failed to fetch storage pricing data. HTTP Status: {response.status_code}")
        return None

def extract_options(storage_data):
    """Extract available storage options from API response."""
    if not storage_data or "offers" not in storage_data:
        print("Invalid API response structure. 'offers' key not found.")
        return {}

    available_regions = set()
    available_storage_types = set()
    available_access_tiers = set()
    available_redundancy = set()

    for key, value in storage_data["offers"].items():
        parts = key.split("-")

        if len(parts) >= 3:
            available_storage_types.add(parts[2])  # Storage Type (blob, file, table, queue)
        
        if len(parts) >= 4:
            available_access_tiers.add(parts[3])  # Access Tier (Hot, Cool, Archive)
        
        if len(parts) >= 5:
            available_redundancy.add(parts[4])    # Redundancy (LRS, ZRS, GRS, etc.)

        # Extract available regions dynamically
        if isinstance(value, dict) and "prices" in value:
            for price_type in value["prices"]:
                if isinstance(value["prices"][price_type], dict):
                    available_regions.update(value["prices"][price_type].keys())

    return {
        "regions": sorted(available_regions),
        "storage_types": sorted(available_storage_types),
        "access_tiers": sorted(available_access_tiers),
        "redundancy": sorted(available_redundancy),
    }

def get_user_selection(options, prompt):
    """Ask the user to select an option from available choices."""
    if not options:
        print(f"No available options for {prompt}. Please check API response.")
        exit(1)

    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    while True:
        try:
            choice = int(input(f"Enter your choice (1-{len(options)}): "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print("Invalid choice. Please select a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def calculate_storage_cost(storage_data, storage_type, access_tier, redundancy, region, capacity):
    """Calculate storage cost based on selection."""
    # Construct pricing key dynamically
    pricing_key = f"general-purpose-v2-{storage_type}-{access_tier}-{redundancy}-capacity"
    
    price_per_gb = None
    if pricing_key in storage_data["offers"]:
        price_entry = storage_data["offers"][pricing_key]
        if "prices" in price_entry:
            for price_type in price_entry["prices"]:
                region_prices = price_entry["prices"][price_type]
                if region in region_prices:
                    price_per_gb = region_prices[region].get("value", None)
                    break  # Stop if price is found

    if price_per_gb is None:
        print(f"No pricing data found for {storage_type} {access_tier} {redundancy} in {region}.")
        return 0, 0

    total_cost = price_per_gb * capacity
    return total_cost, price_per_gb

# Fetch storage pricing
storage_data = fetch_storage_pricing()

if storage_data:
    # Extract available options
    options = extract_options(storage_data)

    if not options:
        print("No storage options found. Exiting.")
        exit(1)

    # Step 1: Select Region
    selected_region = get_user_selection(options["regions"], "Select an Azure region:")

    # Step 2: Select Storage Type
    selected_storage_type = get_user_selection(options["storage_types"], "Select a storage type:")

    # Step 3: Select Access Tier
    selected_access_tier = get_user_selection(options["access_tiers"], "Select an access tier:")

    # Step 4: Select Redundancy Type
    selected_redundancy = get_user_selection(options["redundancy"], "Select a redundancy type:")

    # Step 5: Enter Capacity (GB)
    while True:
        try:
            capacity = float(input("\nEnter storage capacity (in GB): "))
            if capacity > 0:
                break
            else:
                print("Capacity must be a positive number.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

    # Calculate and display cost
    total_cost, price_per_gb = calculate_storage_cost(storage_data, selected_storage_type, selected_access_tier, selected_redundancy, selected_region, capacity)

    print("\nAzure Storage Pricing Summary")
    print(f"Region: {selected_region}")
    print(f"Storage Type: {selected_storage_type}")
    print(f"Access Tier: {selected_access_tier}")
    print(f"Redundancy: {selected_redundancy}")
    print(f"Capacity: {capacity} GB")
    print(f"Price per GB: ${price_per_gb:.4f}")
    print(f"Total Estimated Cost: ${total_cost:.4f}\n")
else:
    print("Failed to fetch storage pricing data.")