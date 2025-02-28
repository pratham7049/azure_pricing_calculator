import requests
import json

# Azure Pricing API Endpoint
STORAGE_PRICING_API = "https://azure.microsoft.com/api/v3/pricing/storage/calculator/?culture=en-in&discount=mca"

def fetch_pricing_data():
    """Fetch storage pricing data from Azure Pricing API."""
    response = requests.get(STORAGE_PRICING_API)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching Azure pricing data.")
        return None

def extract_options(pricing_data):
    """Extract available storage tiers, replication types, and operations dynamically."""
    storage_tiers = set()
    replications = set()
    operation_types = set()

    for offer_key in pricing_data["offers"]:
        parts = offer_key.split("-")
        for part in parts:
            if part in ["hot", "cool", "archive"]:
                storage_tiers.add(part)
            elif part in ["lrs", "zrs", "grs", "ra-grs", "gzrs", "ra-gzrs"]:
                replications.add(part)
            elif "operations" in part:
                operation_types.add(part)

    return list(storage_tiers), list(replications), list(operation_types)

def find_matching_offer(pricing_data, storage_tier, replication, operation_type):
    """Finds the correct pricing key dynamically based on user inputs."""
    for offer_key in pricing_data["offers"]:
        if (
            storage_tier in offer_key
            and replication in offer_key
            and operation_type in offer_key
        ):
            return offer_key
    return None

def get_price_for_offer(pricing_data, offer_key, region):
    """Extract the price for a given offer and region."""
    try:
        return pricing_data["offers"][offer_key]["prices"]["per10k"][region]["value"]
    except KeyError:
        print(f"Pricing not found for {offer_key} in {region}.")
        return None

def calculate_storage_cost(region, storage_tier, replication, storage_size_gb, operations_per_month, pricing_data):
    """Calculate the monthly cost of Azure Storage Account dynamically."""
    
    # Find matching offer keys dynamically
    storage_pricing_key = find_matching_offer(pricing_data, storage_tier, replication, "other-operations")
    operation_pricing_key = find_matching_offer(pricing_data, "general-purpose", "page", "delete-operations")

    if not storage_pricing_key or not operation_pricing_key:
        print("Error: Unable to find correct pricing keys.")
        return None

    # Get Storage Cost per 10K Units
    storage_cost_per_10k = get_price_for_offer(pricing_data, storage_pricing_key, region)
    operation_cost_per_10k = get_price_for_offer(pricing_data, operation_pricing_key, region)

    if storage_cost_per_10k is None or operation_cost_per_10k is None:
        return None

    # Convert GB to TB (Azure pricing often uses TB)
    storage_size_tb = storage_size_gb / 1024

    # Compute Costs
    storage_cost = storage_size_tb * storage_cost_per_10k * 10000  # Convert per 10K to per unit
    operation_cost = (operations_per_month / 10000) * operation_cost_per_10k

    # Total Monthly Cost
    total_cost = storage_cost + operation_cost

    return {
        "region": region,
        "storage_tier": storage_tier,
        "replication": replication,
        "storage_size_gb": storage_size_gb,
        "operations_per_month": operations_per_month,
        "storage_cost": storage_cost,
        "operation_cost": operation_cost,
        "total_monthly_cost": total_cost
    }

# Fetch Pricing Data
pricing_data = fetch_pricing_data()

if pricing_data:
    # Extract available options dynamically
    storage_tiers, replications, operation_types = extract_options(pricing_data)

    # Display options to the user
    print("\nAvailable Storage Tiers:", ", ".join(storage_tiers))
    print("Available Replication Types:", ", ".join(replications))
    print("Available Operation Types:", ", ".join(operation_types))

    # Take user inputs
    region = input("\nEnter Azure region (e.g., us-east, us-west): ").strip()
    storage_tier = input("Select Storage Tier: ").strip().lower()
    replication = input("Select Replication Type: ").strip().lower()
    storage_size_gb = float(input("Enter Storage Size (GB): "))
    operations_per_month = int(input("Enter Number of Operations per Month: "))

    # Calculate Cost
    result = calculate_storage_cost(region, storage_tier, replication, storage_size_gb, operations_per_month, pricing_data)

    if result:
        print("\n===== Azure Storage Pricing Breakdown =====")
        print(json.dumps(result, indent=4))
    else:
        print("Error: Unable to calculate cost.")
