import requests

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
    return {
        "Regions": sorted({r["slug"] for r in data.get("regions", [])}),
        "Storage Types": sorted({s["slug"] for s in data.get("storageTypes", [])}),
        "Performance": sorted({t["slug"] for t in data.get("tiers", [])}),
        "Storage Account Types": sorted({a["slug"] for a in data.get("accountTypes", [])}),
        "File Structure": sorted({f["slug"] for f in data.get("fileStructureTypes", [])}),
        "Access Tiers": sorted({a["slug"] for a in data.get("accessTypes", [])}),
        "Redundancies": sorted({r["slug"] for r in data.get("redundancies", [])}),
    }

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
def get_price(data, region, storage_type, performance, account_type, file_structure, access_tier, redundancy):
    offers = data.get("offers", {})

    for offer_value in offers.values():
        if not isinstance(offer_value, dict):
            continue  # Skip if offer_value is not a dictionary

        # Extract offer details
        offer_region = offer_value.get("region", "").lower()
        offer_storage_type = offer_value.get("storageType", "").lower()
        offer_performance = offer_value.get("tier", "").lower()
        offer_account_type = offer_value.get("accountType", "").lower()
        offer_file_structure = offer_value.get("fileStructure", "").lower()
        offer_access_tier = offer_value.get("accessTier", "").lower()
        offer_redundancy = offer_value.get("redundancy", "").lower()
        price = offer_value.get("price")

        # Match user-selected values with API data
        if (
            offer_region == region and
            offer_storage_type == storage_type and
            offer_performance == performance and
            offer_account_type == account_type and
            offer_file_structure == file_structure and
            offer_access_tier == access_tier and
            offer_redundancy == redundancy
        ):
            return float(price) if price else None  # Return price if available

    return None  # Return None if no matching price is found

# Main Execution
data = fetch_storage_pricing()
if data:
    available_options = list_options(data)

    # Get user selections step-by-step
    selected_region = get_user_selection(available_options, "Regions")
    selected_storage = get_user_selection(available_options, "Storage Types")
    selected_performance = get_user_selection(available_options, "Performance")
    selected_account_type = get_user_selection(available_options, "Storage Account Types")
    selected_file_structure = get_user_selection(available_options, "File Structure")
    selected_access_tier = get_user_selection(available_options, "Access Tiers")
    selected_redundancy = get_user_selection(available_options, "Redundancies")

    # Get capacity input
    capacity = float(input("Enter storage capacity in GB (default 1000 GB): ") or 1000)

    # Fetch price
    price_per_gb = get_price(
        data, selected_region, selected_storage, selected_performance, 
        selected_account_type, selected_file_structure, selected_access_tier, selected_redundancy
    )

    if price_per_gb is None:
        print("\nNo matching price found for the selected options.")
    else:
        total_price = price_per_gb * capacity
        print(f"\nPrice per GB: {price_per_gb}")
        print(f"Total Estimated Price for {capacity} GB: {total_price}")
