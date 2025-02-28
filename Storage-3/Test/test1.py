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
        "reservations": {key: key for key in data["offers"] if "reserved-capacity" in key.lower()}  # Extract reservation plans
    }

    available_operations = [key for key in data["offers"] if "operation" in key.lower()]
    options["operations"] = {op: op for op in available_operations}

    return options

def get_price_from_offer(offer, region, capacity_gb):
    """Retrieves price from offer data safely, supporting both flat and graduated pricing."""
    price_data = offer.get("prices", {}).get("pergb", {}).get(region, {}).get("value")
    return price_data if price_data is not None else 0

def get_reservation_price(offers, reservation_key, region):
    """Fetches reservation cost and converts yearly to monthly if needed."""
    reservation_offer = offers.get(reservation_key)

    if not reservation_offer:
        print(f"[ERROR] Reservation offer '{reservation_key}' NOT found.")
        return 0

    # Identify the pricing key for reservation
    pricing_keys = list(reservation_offer.get("prices", {}).keys())

    if not pricing_keys:
        print(f"[WARNING] No pricing keys found for reservation '{reservation_key}'.")
        return 0

    # Determine if it's a 1-year or 3-year reservation
    if "oneyear" in reservation_key:
        reservation_type_key = next((key for key in pricing_keys if "peroneyear" in key.lower()), None)
        divisor = 12  # Convert yearly to monthly
    elif "threeyear" in reservation_key:
        reservation_type_key = next((key for key in pricing_keys if "perthreeyear" in key.lower()), None)
        divisor = 36  # Convert 3-year to monthly
    else:
        reservation_type_key = pricing_keys[0]  # Default to first key
        divisor = 1  # Assume monthly if format unknown

    if not reservation_type_key:
        print(f"[WARNING] No valid reservation type key found for '{reservation_key}'")
        return 0

    price_data = reservation_offer["prices"].get(reservation_type_key, {}).get(region, {}).get("value")

    if price_data is None:
        print(f"[WARNING] No reservation pricing found for {reservation_key} in {region}")
        return 0

    return price_data / divisor  # Convert to monthly cost

def calculate_cost(offers, offer_key_storage, offer_key_operations, offer_key_reservation, region, capacity_gb, num_operations):
    """Calculates total cost based on selected options."""

    storage_offer = offers.get(offer_key_storage)
    operation_offer = offers.get(offer_key_operations)
    reservation_offer = offers.get(offer_key_reservation)

    if not storage_offer:
        print(f"[ERROR] Storage offer key '{offer_key_storage}' NOT found.")
        return

    if not operation_offer:
        print(f"[ERROR] Operation offer key '{offer_key_operations}' NOT found.")
        return

    if not reservation_offer:
        print(f"[ERROR] Reservation offer key '{offer_key_reservation}' NOT found.")
        return

    # Get prices
    storage_price_gb = get_price_from_offer(storage_offer, region, capacity_gb)
    operation_price = get_price_from_offer(operation_offer, region, 0)  # Operations aren't tiered
    reservation_cost = get_reservation_price(offers, offer_key_reservation, region)

    # Compute costs
    total_storage_cost = capacity_gb * storage_price_gb
    total_operation_cost = num_operations * operation_price
    total_cost = total_storage_cost + total_operation_cost + reservation_cost

    print("\n=== Azure Storage Pricing Calculation ===")
    print(f"Region: {region}")
    print(f"Storage Type: {offer_key_storage}")
    print(f"Capacity: {capacity_gb} GB")
    print(f"Operations: {num_operations}")
    print(f"Reservation Plan: {offer_key_reservation}")

    print("\n=== Pricing Breakdown ===")
    print(f"Price per GB: ${storage_price_gb:.6f} -> Total Storage Cost: ${total_storage_cost:.2f}")
    print(f"Price per Operation: ${operation_price:.6f} -> Total Operations Cost: ${total_operation_cost:.2f}")
    print(f"Reservation Cost (monthly): ${reservation_cost:.2f}")

    print(f"\nTotal Monthly Cost: ${total_cost:.2f}")

def main():
    pricing_data = fetch_pricing_data()
    if not pricing_data:
        return

    options = extract_options(pricing_data)
    
    # User selections
    region = get_user_selection(options["regions"], "Region")
    account_type = get_user_selection(options["account_types"], "Account Type")
    storage_type = get_user_selection(options["storage_types"], "Storage Type")
    access_tier = get_user_selection(options["access_tiers"], "Access Tier")
    redundancy = get_user_selection(options["redundancies"], "Redundancy")
    file_structure = get_user_selection(options["file_structures"], "File Structure")
    operation_type = get_user_selection(options["operations"], "Operation Type")
    reservation_type = get_user_selection(options["reservations"], "Reservation Type")

    capacity_gb = float(input("Enter Storage Capacity in GB: "))
    num_operations = int(input("Enter Number of Operations: "))

    # Finding best match offer keys
    offer_key_storage = f"{account_type}-{storage_type}-{file_structure}-{access_tier}-{redundancy}"
    offer_key_operations = operation_type  # Already in correct format
    offer_key_reservation = reservation_type  # Direct selection

    # Calculate cost
    calculate_cost(pricing_data["offers"], offer_key_storage, offer_key_operations, offer_key_reservation, region, capacity_gb, num_operations)

if __name__ == "__main__":
    main()
