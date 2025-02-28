import requests

# Azure Pricing API
API_URL = "https://azure.microsoft.com/api/v3/pricing/storage/calculator/?culture=en-in&discount=mca"

# Fetch API Data
def fetch_pricing_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"[ERROR] Failed to fetch pricing data. Status Code: {response.status_code}")
        return None

# Get user selections dynamically
def get_user_selection(options, prompt):
    print(f"\nAvailable {prompt}: {', '.join(options)}")
    choice = input(f"Enter {prompt.replace('_', ' ')}: ").strip().lower()
    while choice not in options:
        print("[ERROR] Invalid selection. Try again.")
        choice = input(f"Enter {prompt.replace('_', ' ')}: ").strip().lower()
    return choice

# Extract available selections from API data
def extract_options(data):
    return {
        "regions": {item["slug"]: item["displayName"] for item in data["regions"]},
        "storage_types": {item["slug"]: item["displayName"] for item in data["storageTypes"]},
        "account_types": {item["slug"]: item["displayName"] for item in data["accountTypes"]},
        "access_tiers": {item["slug"]: item["displayName"] for item in data["accessTypes"]},
        "redundancies": {item["slug"]: item["displayName"] for item in data["redundancies"]},
        "file_structures": {item["slug"]: item["displayName"] for item in data.get("fileStructureTypes", [])}
    }

# Calculate cost dynamically
def calculate_cost(offers, offer_key_storage, offer_key_operations, region, capacity_gb, num_operations):
    print("\nChecking Offer Keys")
    print(f"Offer Key for Storage: {offer_key_storage}")
    print(f"Offer Key for Operations: {offer_key_operations}")

    # Debug: Print all available offer keys
    print("\n=== Available Offer Keys in API Response ===")
    for key in offers.keys():
        print(key)

    # Fetch storage and operation pricing
    storage_offer = offers.get(offer_key_storage, {})
    operation_offer = offers.get(offer_key_operations, {})

    # Storage Pricing
    storage_price = storage_offer.get("prices", {}).get("perGB", {}).get(region, {}).get("value", 0) or \
                    storage_offer.get("prices", {}).get("perTB", {}).get(region, {}).get("value", 0) / 1000  # Convert per TB to per GB if necessary

    # Operation Pricing
    operation_price = operation_offer.get("prices", {}).get("per10k", {}).get(region, {}).get("value", 0) / 10000

    # Error handling for missing pricing
    if storage_price == 0:
        print(f"\n[ERROR] Storage offer key '{offer_key_storage}' NOT found in API response.")
    if operation_price == 0:
        print(f"\n[ERROR] Operation offer key '{offer_key_operations}' NOT found in API response.")

    # Compute Total Cost
    total_storage_cost = capacity_gb * storage_price
    total_operation_cost = num_operations * operation_price
    total_cost = total_storage_cost + total_operation_cost

    # Print final cost breakdown
    print("\n=== Azure Storage Pricing Calculation ===")
    print(f"Region: {region}")
    print(f"Storage Type: {offer_key_storage}")
    print(f"Performance: Standard")
    print(f"Storage Account Type: General Purpose V2")
    print(f"File Structure: Flat Namespace")
    print(f"Access Tier: Hot")
    print(f"Redundancy: LRS")
    print(f"Capacity: {capacity_gb} GB")
    print(f"Operations: {num_operations}")

    print("\n=== Pricing Breakdown ===")
    print(f"Price per GB: ${storage_price} -> Total Storage Cost: ${total_storage_cost:.2f}")
    print(f"Price per Operation: ${operation_price} -> Total Operations Cost: ${total_operation_cost:.2f}")

    print(f"\nTotal Monthly Cost: ${total_cost:.2f}")

# Main Function
def main():
    # Fetch Azure pricing data
    pricing_data = fetch_pricing_data()
    if not pricing_data:
        return

    # Extract available options
    options = extract_options(pricing_data)

    # Get user input
    region = get_user_selection(options["regions"], "Region")
    storage_type = get_user_selection(options["storage_types"], "Storage Type")
    account_type = get_user_selection(options["account_types"], "Storage Account Type")
    access_tier = get_user_selection(options["access_tiers"], "Access Tier")
    redundancy = get_user_selection(options["redundancies"], "Redundancy")
    file_structure = get_user_selection(options["file_structures"], "File Structure")

    capacity_gb = float(input("Enter Storage Capacity in GB: "))
    num_operations = int(input("Enter Number of Operations: "))

    # Generate Offer Keys
    offer_key_storage = f"{account_type}-{storage_type}-{file_structure}-{access_tier}-{redundancy}"
    offer_key_operations = f"{account_type}-{storage_type}-{file_structure}-{access_tier}-{redundancy}"

    # Calculate total cost
    calculate_cost(pricing_data["offers"], offer_key_storage, offer_key_operations, region, capacity_gb, num_operations)

if __name__ == "__main__":
    main()
