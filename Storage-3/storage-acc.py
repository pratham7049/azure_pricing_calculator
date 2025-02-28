import requests

# Azure Pricing API endpoint
STORAGE_URL = "https://azure.microsoft.com/api/v3/pricing/storage/calculator/?culture=en-in&discount=mca"

def fetch_storage_pricing():
    """Fetch storage pricing data from Azure API"""
    response = requests.get(STORAGE_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch storage pricing data.")
        return None

def list_available_options(storage_data):
    """List available storage tiers, replication types, operations, and regions"""
    available_tiers = set()
    available_replication = set()
    available_operations = set()
    available_regions = set()

    for key, value in storage_data["offers"].items():
        parts = key.split("-")
        if len(parts) >= 6:
            available_tiers.add(parts[4])         # Extract storage tier
            available_replication.add(parts[5])   # Extract replication type
        available_operations.add(key)            # Store operation type

        # Extract regions dynamically
        if "prices" in value:
            for price_type in value["prices"]:  # This can be 'per10k' or other keys
                if isinstance(value["prices"][price_type], dict):
                    available_regions.update(value["prices"][price_type].keys())

    return sorted(available_tiers), sorted(available_replication), sorted(available_operations), sorted(available_regions)

def get_user_selection(options, prompt):
    """Display numbered options for user selection, ensuring options exist"""
    if not options:
        print(f"No available options for {prompt}. Please check the API response.")
        exit(1)  # Exit the script if no options are available

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

def get_pricing(storage_data, storage_tier, replication, operation_key, region, usage_count):
    """Calculate pricing dynamically based on user selection"""
    storage_pricing_key = f"general-purpose-v2-block-blob-structured-{storage_tier}-{replication}-other-operations"
    
    price_per_10k = 0
    if storage_pricing_key in storage_data["offers"]:
        price_entry = None
        if "prices" in storage_data["offers"][storage_pricing_key]:
            for price_type in storage_data["offers"][storage_pricing_key]["prices"]:
                price_entry = storage_data["offers"][storage_pricing_key]["prices"][price_type].get(region, {})
                if price_entry:
                    break  # Stop at first found price

        price_per_10k = price_entry.get("value", 0) if isinstance(price_entry, dict) else 0

    # Fetch operation pricing safely
    operation_price_entry = None
    if operation_key in storage_data["offers"]:
        if "prices" in storage_data["offers"][operation_key]:
            for price_type in storage_data["offers"][operation_key]["prices"]:
                operation_price_entry = storage_data["offers"][operation_key]["prices"][price_type].get(region, {})
                if operation_price_entry:
                    break  # Stop at first found price

    operation_price = operation_price_entry.get("value", 0) if isinstance(operation_price_entry, dict) else 0

    # Calculate total cost
    total_cost = ((usage_count / 10000) * price_per_10k) + ((usage_count / 10000) * operation_price)
    return total_cost

# Fetch data
storage_data = fetch_storage_pricing()

if storage_data:
    # List available options dynamically
    tiers, replication_types, operations, regions = list_available_options(storage_data)

    # Ensure regions are available before proceeding
    if not regions:
        print("No regions available in the API response. Exiting...")
        exit(1)

    # Get user selections with numbered options
    selected_tier = get_user_selection(tiers, "Select a storage tier:")
    selected_replication = get_user_selection(replication_types, "Select a replication type:")
    selected_operation = get_user_selection(operations, "Select an operation type:")
    selected_region = get_user_selection(regions, "Select an Azure region:")
    usage = float(input("Enter the number of operations (e.g., 100000): "))

    # Calculate and display cost
    cost = get_pricing(storage_data, selected_tier, selected_replication, selected_operation, selected_region, usage)
    
    if cost is not None:
        print(f"\nTotal estimated cost: ${cost:.4f}")
