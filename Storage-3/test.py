import requests
import json

# Azure Storage Pricing API URL
API_URL = "https://azure.microsoft.com/api/v3/pricing/storage/calculator/?culture=en-in&discount=mca&billingAccount=&billingProfile=&v=20250219-1155-433953"

# Fetch data from the Azure Pricing API
def fetch_storage_pricing():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch data:", response.status_code)
        return None

# Extract and display available options dynamically
def list_options(data):
    options = {
        "Regions": sorted({r["slug"] for r in data.get("regions", [])}),
        "Storage Types": sorted({s["slug"] for s in data.get("storageTypes", [])}),
        "Access Types": sorted({a["slug"] for a in data.get("accessTypes", [])}),
        "Redundancies": sorted({r["slug"] for r in data.get("redundancies", [])}),
        "Tiers": sorted({t["slug"] for t in data.get("tiers", [])}),
        "Account Types": sorted({a["slug"] for a in data.get("accountTypes", [])}),
    }
    return options

# Function to prompt user for selection
def get_user_selection(options, key):
    print(f"\nAvailable {key}:")
    for name in options[key]:
        print(f"  - {name}")

    while True:
        selected = input(f"Enter your choice for {key}: ").strip().lower()
        if selected in options[key]:
            return selected
        print("Invalid selection, please try again.")

# Get pricing from the offers section
def get_price(data, region, storage_type, access_type, redundancy, tier):
    offers = data.get("offers", {})

    # Iterate through offers to find the matching price
    for offer_key, offer_value in offers.items():
        if not isinstance(offer_value, dict):
            continue  # Skip if offer_value is not a dictionary

        # Extract offer details
        offer_region = offer_value.get("region", "").lower()
        offer_storage_type = offer_value.get("storageType", "").lower()
        offer_access_type = offer_value.get("accessTier", "").lower()
        offer_redundancy = offer_value.get("redundancy", "").lower()
        offer_tier = offer_value.get("tier", "").lower()
        price = offer_value.get("price")

        # Match user-selected values with API data
        if (
            offer_region == region and
            offer_storage_type == storage_type and
            offer_access_type == access_type and
            offer_redundancy == redundancy and
            offer_tier == tier
        ):
            if price:
                return float(price)  # Return the extracted price if available

    return None  # Return None if no matching price is found

# Main Execution
data = fetch_storage_pricing()
if data:
    available_options = list_options(data)

    # Get user input step-by-step
    selected_region = get_user_selection(available_options, "Regions")
    selected_storage = get_user_selection(available_options, "Storage Types")
    selected_access = get_user_selection(available_options, "Access Types")
    selected_redundancy = get_user_selection(available_options, "Redundancies")
    selected_tier = get_user_selection(available_options, "Tiers")

    quantity = float(input("Enter the quantity (e.g., TB, GB, operations): "))

    # Fetch price
    price_per_unit = get_price(data, selected_region, selected_storage, selected_access, selected_redundancy, selected_tier)

    if price_per_unit is None:
        print("\nNo matching price found for the selected options.")
    else:
        total_price = price_per_unit * quantity
        print(f"\nPrice per unit: {price_per_unit}")
        print(f"Total Estimated Price: {total_price}")
