import requests

AZURE_STORAGE_PRICING_URL = "https://azure.microsoft.com/api/v3/pricing/storage/calculator/?culture=en-in&discount=mca"

def fetch_azure_storage_pricing():
    """Fetches Azure Storage pricing from the API."""
    response = requests.get(AZURE_STORAGE_PRICING_URL)
    if response.status_code != 200:
        print("[ERROR] Failed to fetch Azure pricing data.")
        return None
    return response.json()

def get_price_from_offer(offer, region, is_operation=False):
    """Retrieves price from offer data, handling both storage and operations pricing."""
    if not offer:
        print("[ERROR] Offer data missing!")
        return 0

    print(f"\n[DEBUG] Checking offer: {offer.get('id', 'Unknown')}")
    print(f"[DEBUG] Available Pricing Keys: {offer.get('prices', {}).keys()}")

    # Define pricing keys for different cases
    price_keys = ["perOperation", "per10kOperations", "per100kOperations", "per10k"] if is_operation else ["pergb"]

    for key in price_keys:
        if key in offer["prices"]:
            if region in offer["prices"][key]:  # ✅ Fix: Now correctly checking for region inside per10k
                price = offer["prices"][key][region].get("value", 0)
                print(f"[DEBUG] Found {key} price in {region}: {price}")
                return price  # No division, return exact API price

    print(f"[WARNING] No valid price found for {region}.")
    return 0

    print(f"[WARNING] No valid price found for {region}.")
    return 0

def list_available_options(storage_data):
    """Extracts and lists available storage types and operation types."""
    storage_types = list(storage_data["offers"].keys())
    return {
        "storage_types": storage_types,
        "operation_types": storage_types  # Since operations are also under the same structure
    }

def get_user_selection(options, prompt):
    """Prompts user to select an option and returns the slug."""
    print(f"\nAvailable {prompt}:")
    print("  ", " | ".join(options))  # Display only slug values
    selection = input(f"Enter {prompt} (slug): ").strip()
    while selection not in options:
        print("[ERROR] Invalid selection. Try again.")
        selection = input(f"Enter {prompt} (slug): ").strip()
    return selection

def main():
    """Main function to calculate Azure Storage pricing."""
    print("Fetching Azure Pricing Data...")
    azure_pricing = fetch_azure_storage_pricing()
    if not azure_pricing:
        return

    offers = azure_pricing.get("offers", {})
    options = list_available_options(azure_pricing)

    # Step 1: Get user input
    storage_type = get_user_selection(options["storage_types"], "Storage Type")
    operation_type = get_user_selection(options["operation_types"], "Operation Type")

    capacity_gb = float(input("Enter Storage Capacity in GB: "))
    num_operations = int(input("Enter Number of Operations: "))

    # Step 2: Extract storage and operation pricing
    storage_offer = offers.get(storage_type, {})
    operation_offer = offers.get(operation_type, {})

    region = "us-east"  # Hardcoded for now, can be made user-selectable

    storage_price_per_gb = get_price_from_offer(storage_offer, region, is_operation=False)
    operation_price_per_op = get_price_from_offer(operation_offer, region, is_operation=True)

    # Step 3: Calculate costs
    storage_cost = storage_price_per_gb * capacity_gb
    operation_cost = operation_price_per_op * num_operations
    total_cost = storage_cost + operation_cost

    # Step 4: Display Results
    print("\n=== Azure Storage Pricing Calculation ===")
    print(f"Region: {region}")
    print(f"Storage Type: {storage_type}")
    print(f"Operations Type: {operation_type}")
    print(f"Capacity: {capacity_gb} GB")
    print(f"Operations: {num_operations}\n")

    print("=== Pricing Breakdown ===")
    print(f"Storage Cost: ${storage_cost:.2f} (Price per GB: ${storage_price_per_gb:.6f})")
    print(f"Operation Cost: ${operation_cost:.6f} (Price per Operation: ${operation_price_per_op:.9f})")

    print("\nTotal Monthly Cost: ${:.6f}".format(total_cost))

if __name__ == "__main__":
    main()
