import requests
import json

API_URL = "https://azure.microsoft.com/api/v3/pricing/storage/calculator/?culture=en-in&discount=mca"

def fetch_pricing_data():
    """Fetch Azure Storage Pricing Data."""
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

    # Extract available operation types
    options["operations"] = {key: key for key in data["offers"] if "operation" in key.lower()}

    return options

def find_best_matching_offer(pricing_data, account_type, storage_type, access_tier, redundancy, file_structure):
    """Finds the best matching storage offer key dynamically."""
    expected_key = f"{account_type}-{storage_type}-{file_structure}-{access_tier}-{redundancy}"

    print("\n[DEBUG] Searching for match using:")
    print(f"  Expected Key: {expected_key}")

    exact_match = None
    partial_match = None

    for key in pricing_data["offers"]:
        if "operation" in key.lower():
            continue  # Skip operation keys

        if key == expected_key:
            exact_match = key
            break  # Stop searching if exact match found
        
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

def get_price_from_offer(offer, region, units):
    """Retrieves price from offer data based on available units."""
    for unit in units:
        if unit in offer.get("prices", {}):
            return offer["prices"][unit].get(region, {}).get("value", 0)
    return 0  # Default to 0 if no price found

def calculate_cost(offers, offer_key_storage, region, capacity_gb, operation_costs):
    """Calculates total cost for storage and operations."""
    print("\nChecking Offer Keys")
    print(f"Offer Key for Storage: {offer_key_storage}")

    storage_offer = offers.get(offer_key_storage)

    if not storage_offer:
        print(f"[ERROR] Storage offer key '{offer_key_storage}' NOT found in API response.")
        return

    # Get storage cost per GB
    storage_price_gb = get_price_from_offer(storage_offer, region, ["pergb"])
    total_storage_cost = capacity_gb * storage_price_gb

    # Compute total operation costs
    total_operation_cost = sum(operation_costs.values())

    # Final cost
    total_cost = total_storage_cost + total_operation_cost

    print("\n=== Azure Storage Pricing Calculation ===")
    print(f"Region: {region}")
    print(f"Storage Type: {offer_key_storage}")
    print(f"Capacity: {capacity_gb} GB")

    print("\n=== Pricing Breakdown ===")
    print(f"Price per GB: ${storage_price_gb:.6f} -> Total Storage Cost: ${total_storage_cost:.2f}")

    for op_type, cost in operation_costs.items():
        print(f"{op_type} Cost: ${cost:.2f}")

    print(f"\nTotal Monthly Cost: ${total_cost:.2f}")

def main():
    pricing_data = fetch_pricing_data()
    if not pricing_data:
        return

    options = extract_options(pricing_data)

    # Select Storage Parameters
    region = get_user_selection(options["regions"], "Region")
    account_type = get_user_selection(options["account_types"], "Account Type")
    storage_type = get_user_selection(options["storage_types"], "Storage Type")
    access_tier = get_user_selection(options["access_tiers"], "Access Tier")
    redundancy = get_user_selection(options["redundancies"], "Redundancy")
    file_structure = get_user_selection(options["file_structures"], "File Structure")

    capacity_gb = float(input("Enter Storage Capacity in GB: "))

    # Find best matching offer key for storage
    offer_key_storage = find_best_matching_offer(pricing_data, account_type, storage_type, access_tier, redundancy, file_structure)
    if not offer_key_storage:
        return

    # Select operations
    operation_costs = {}
    while True:
        print("\n=== Select an Operation ===")
        operation_type = get_user_selection(options["operations"], "Operation Type")

        if operation_type is None:
            break

        num_operations = int(input(f"Enter number of {operation_type} operations: "))

        # Get operation cost dynamically
        operation_offer = pricing_data["offers"].get(operation_type)
        if not operation_offer:
            print(f"[ERROR] Operation offer '{operation_type}' not found in API.")
            continue

        operation_price = get_price_from_offer(operation_offer, region, ["peroperation", "per100", "per1000", "per10k"])
        operation_cost = num_operations * operation_price
        operation_costs[operation_type] = operation_cost

        print(f"\n{num_operations} × ${operation_price:.6f} per operation = ${operation_cost:.2f}")

        # Ask if user wants to add more operations
        add_more = input("Do you want to add another operation? (yes/no): ").strip().lower()
        if add_more != "yes":
            break

    # Calculate total cost
    calculate_cost(pricing_data["offers"], offer_key_storage, region, capacity_gb, operation_costs)

if __name__ == "__main__":
    main()
