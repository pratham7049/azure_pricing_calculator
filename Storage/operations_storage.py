import requests

STORAGE_API_URL = "https://azure.microsoft.com/api/v3/pricing/storage/calculator/?culture=en-in&discount=mca"

def fetch_azure_storage_pricing():
    """Fetches storage pricing data from the Azure API."""
    response = requests.get(STORAGE_API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print("[ERROR] Failed to fetch Azure Pricing data.")
        return None

def extract_options(available_operations):
    """Extracts unique options for each category from operation slugs."""
    options = {
        "account_type": set(),
        "storage_type": set(),
        "blob_type": set(),
        "tier": set(),
        "replication_type": set(),
        "operation_type": set()
    }

    for operation in available_operations:
        parts = operation.split("-")
        if len(parts) >= 6:
            options["account_type"].add(parts[0] + "-" + parts[1])
            options["storage_type"].add(parts[2])
            options["blob_type"].add(parts[3])
            options["tier"].add(parts[4])
            options["replication_type"].add(parts[5])
            options["operation_type"].add("-".join(parts[6:]))

    return {key: sorted(value) for key, value in options.items()}

def select_option(prompt, options):
    """Prompts the user to select an option from available choices."""
    print(f"\n{prompt}")
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")

    while True:
        try:
            choice = int(input("Enter choice: "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print("[ERROR] Invalid selection. Try again.")
        except ValueError:
            print("[ERROR] Please enter a valid number.")

def get_price_from_offer(offer, region):
    """Retrieves price based on operation type."""
    if not offer or "prices" not in offer:
        return None  # No valid offer

    for unit in ["peroperation", "per100", "per1000", "per10k", "per10000", "per1000000"]:
        if unit in offer["prices"]:
            unit_price = offer["prices"][unit].get(region, {}).get("value", 0)
            if unit_price > 0:
                return unit_price, unit  # Return price and unit type
    
    return None, None  # No valid price found

def main():
    """Main execution function."""
    storage_data = fetch_azure_storage_pricing()
    if not storage_data:
        return

    available_operations = list(storage_data["offers"].keys())
    extracted_options = extract_options(available_operations)

    # Step-by-step user input selection
    account_type = select_option("Select Account Type:", extracted_options["account_type"])
    storage_type = select_option("Select Storage Type:", extracted_options["storage_type"])
    blob_type = select_option("Select Blob Type:", extracted_options["blob_type"])
    tier = select_option("Select Storage Tier:", extracted_options["tier"])
    replication_type = select_option("Select Replication Type:", extracted_options["replication_type"])
    operation_type = select_option("Select Operation Type:", extracted_options["operation_type"])

    operation_slug = f"{account_type}-{storage_type}-{blob_type}-{tier}-{replication_type}-{operation_type}"
    print(f"\nSelected Operation: {operation_slug}")

    # Get available regions
    first_offer = next(iter(storage_data["offers"].values()))
    available_regions = list(next(iter(first_offer["prices"].values())).keys())

    region = select_option("Select Region:", available_regions)

    try:
        num_operations = int(input("Enter Number of Operations: "))
    except ValueError:
        print("[ERROR] Invalid number of operations.")
        return

    operation_offer = storage_data["offers"].get(operation_slug)
    if not operation_offer:
        print(f"[ERROR] No valid storage offer found for {operation_slug}")
        return

    unit_price, unit_type = get_price_from_offer(operation_offer, region)
    
    if unit_price is None:
        print("[ERROR] No valid price found.")
        return

    total_cost = num_operations * unit_price  # Only multiplication, no division

    # Display result in Azure-style format
    print("\n=== Pricing Breakdown ===")
    print(f"{num_operations} × ${unit_price:.3f} = ${total_cost:.2f}")
    print(f"Region: {region}")
    print(f"Operation Type: {operation_slug}")
    print(f"Number of Operations: {num_operations}")
    print(f"Total Operations Cost: ${total_cost:.2f}")

if __name__ == "__main__":
    main()
