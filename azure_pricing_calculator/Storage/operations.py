import requests
import json

# Azure Pricing API Endpoint
STORAGE_API_URL = "https://azure.microsoft.com/api/v3/pricing/storage/calculator/?culture=en-in&discount=mca"

def fetch_azure_storage_pricing():
    """Fetches storage pricing data from the Azure API."""
    response = requests.get(STORAGE_API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print("[ERROR] Failed to fetch Azure Pricing data.")
        return None

def get_price_from_offer(offer, region):
    """Retrieves price based on operation type."""
    if not offer or "prices" not in offer:
        return None  # No valid offer

    for unit in ["peroperation", "per100", "per1000", "per10k"]:
        if unit in offer["prices"]:
            unit_price = offer["prices"][unit].get(region, {}).get("value", 0)
            if unit_price > 0:
                return unit_price, unit  # Return price and unit type
    
    return None, None  # No valid price found

def list_available_operations(storage_data):
    """Lists all available operation types."""
    operations = list(storage_data["offers"].keys())
    print("\n=== Available Operations ===")
    for op in operations:
        print(op)
    return operations

def main():
    """Main execution function."""
    storage_data = fetch_azure_storage_pricing()
    if not storage_data:
        return

    available_operations = list_available_operations(storage_data)

    # User selects operation type
    operation_type = input("\nEnter Operation Type (slug): ").strip()
    if operation_type not in available_operations:
        print("[ERROR] Invalid operation type.")
        return

    first_offer = next(iter(storage_data["offers"].values()))
    available_regions = list(next(iter(first_offer["prices"].values())).keys())

    print("\n=== Available Regions ===")
    for region in available_regions:
        print(region)
    region = input("\nEnter Region: ").strip()
    if region not in available_regions:
        print("[ERROR] Invalid region.")
        return

    try:
        num_operations = int(input("Enter Number of Operations: "))
    except ValueError:
        print("[ERROR] Invalid number of operations.")
        return

    operation_offer = storage_data["offers"].get(operation_type)
    if not operation_offer:
        print(f"[ERROR] No valid storage offer found for {operation_type}")
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
    print(f"Operation Type: {operation_type}")
    print(f"Number of Operations: {num_operations}")
    print(f"Total Operations Cost: ${total_cost:.2f}")

if __name__ == "__main__":
    main()
