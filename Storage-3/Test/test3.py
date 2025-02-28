import requests
import json

API_URL = "https://azure.microsoft.com/api/v3/pricing/storage/calculator/?culture=en-in&discount=mca"

def fetch_pricing_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"[ERROR] Failed to fetch pricing data. Status Code: {response.status_code}")
        return None

def get_user_selection(options, prompt):
    """Prompts user to select an option from available choices."""
    if not options:
        print(f"[WARNING] No available {prompt}. Skipping selection.")
        return None

    print(f"\nAvailable {prompt} (slugs): {', '.join(options.keys())}")

    while True:
        choice = input(f"Enter {prompt.replace('_', ' ')} (slug): ").strip().lower()

        if choice in options:
            return choice

        print("[ERROR] Invalid selection. Try again.")

def extract_options(data):
    """Extracts available selection options from the API data."""
    options = {
        "regions": {item["slug"]: item["displayName"] for item in data["regions"]},
        "account_types": {item["slug"]: item["displayName"] for item in data["accountTypes"]},
        "storage_types": {item["slug"]: item["displayName"] for item in data["storageTypes"]},
        "access_tiers": {item["slug"]: item["displayName"] for item in data["accessTypes"]},
        "redundancies": {item["slug"]: item["displayName"] for item in data["redundancies"]},
        "file_structures": {item["slug"]: item["displayName"] for item in data.get("fileStructureTypes", [])},
    }

    available_operations = [key for key in data["offers"] if "operation" in key.lower()]
    options["operations"] = {op: op for op in available_operations}

    return options

def debug_available_offers(pricing_data):
    """Prints all available storage offers to check correct format."""
    print("\n[DEBUG] Available Storage Offers in API:")
    for key in pricing_data["offers"]:
        if "operation" not in key.lower():  # Filter out operation keys
            print(f"  - {key}")

def find_best_matching_offer(pricing_data, account_type, storage_type, access_tier, redundancy, file_structure):
    """Finds the best matching offer key dynamically using flexible pattern matching."""
    expected_key = f"{account_type}-{storage_type}-{file_structure}-{access_tier}-{redundancy}"
    
    print("\n[DEBUG] Searching for match using:")
    print(f"  Expected Key: {expected_key}")

    exact_match = None
    partial_match = None

    for key in pricing_data["offers"]:
        if "operation" in key.lower():
            continue  # Skip operation pricing keys
        
        # Exact match
        if key == expected_key:
            exact_match = key
            break  # Stop searching if we find an exact match
        
        # Partial match (ignore file structure if needed)
        alternative_key = f"{account_type}-{storage_type}-{access_tier}-{redundancy}"
        if alternative_key in key:
            partial_match = key

    if exact_match:
        print(f"[INFO] Exact match found: {exact_match}")
        return exact_match
    elif partial_match:
        print(f"[WARNING] No exact match. Using closest match: {partial_match}")
        return partial_match
    else:
        print(f"[ERROR] No valid storage offer found for {expected_key}")
        return None

def get_price_from_offer(offer, region, price_key):
    """Retrieves price from offer data safely."""
    return offer.get("prices", {}).get(price_key, {}).get(region, {}).get("value", 0)

def calculate_cost(offers, offer_key_storage, offer_key_operations, region, capacity_gb, num_operations):
    """Calculates total cost based on selected options."""
    print("\nChecking Offer Keys")
    print(f"Offer Key for Storage: {offer_key_storage}")
    print(f"Offer Key for Operations: {offer_key_operations}")

    storage_offer = offers.get(offer_key_storage)
    operation_offer = offers.get(offer_key_operations)

    if not storage_offer:
        print(f"[ERROR] Storage offer key '{offer_key_storage}' NOT found in API response.")
        return

    if not operation_offer:
        print(f"[ERROR] Operation offer key '{offer_key_operations}' NOT found in API response.")
        return

    # Fetch storage price (try per GB first, then per TB)
    storage_price_gb = get_price_from_offer(storage_offer, region, "pergb")
    if storage_price_gb == 0:
        storage_price_tb = get_price_from_offer(storage_offer, region, "pertb")
        storage_price_gb = storage_price_tb / 1000  # Convert per TB to per GB

    if storage_price_gb == 0:
        print(f"[ERROR] No valid per-GB or per-TB price found for '{offer_key_storage}' in {region}")
        return

    # Fetch operation price (try per 10k, then per operation)
    operation_price = get_price_from_offer(operation_offer, region, "per10k") / 10000
    if operation_price == 0:
        operation_price = get_price_from_offer(operation_offer, region, "peroperation")

    # Calculate total costs
    total_storage_cost = capacity_gb * storage_price_gb
    total_operation_cost = num_operations * operation_price
    total_cost = total_storage_cost + total_operation_cost

    print("\n=== Azure Storage Pricing Calculation ===")
    print(f"Region: {region}")
    print(f"Storage Type: {offer_key_storage}")
    print(f"Capacity: {capacity_gb} GB")
    print(f"Operations: {num_operations}")

    print("\n=== Pricing Breakdown ===")
    print(f"Price per GB: ${storage_price_gb:.6f} -> Total Storage Cost: ${total_storage_cost:.2f}")
    print(f"Price per Operation: ${operation_price:.6f} -> Total Operations Cost: ${total_operation_cost:.2f}")

    print(f"\nTotal Monthly Cost: ${total_cost:.2f}")

def main():
    pricing_data = fetch_pricing_data()
    if not pricing_data:
        return

    debug_available_offers(pricing_data)  # Print all available offer keys

    options = extract_options(pricing_data)

    region = get_user_selection(options["regions"], "Region")
    account_type = get_user_selection(options["account_types"], "Account Type")
    storage_type = get_user_selection(options["storage_types"], "Storage Type")
    access_tier = get_user_selection(options["access_tiers"], "Access Tier")
    redundancy = get_user_selection(options["redundancies"], "Redundancy")
    file_structure = get_user_selection(options["file_structures"], "File Structure")
    operation_type = get_user_selection(options["operations"], "Operation Type")

    capacity_gb = float(input("Enter Storage Capacity in GB: "))
    num_operations = int(input("Enter Number of Operations: "))

    # Find the best-matching offer key dynamically
    offer_key_storage = find_best_matching_offer(pricing_data, account_type, storage_type, access_tier, redundancy, file_structure)

    if not offer_key_storage:
        return

    if offer_key_storage not in pricing_data["offers"]:
        print(f"[ERROR] Offer key '{offer_key_storage}' not found.")
        return

    calculate_cost(pricing_data["offers"], offer_key_storage, operation_type, region, capacity_gb, num_operations)

if __name__ == "__main__":
    main()
