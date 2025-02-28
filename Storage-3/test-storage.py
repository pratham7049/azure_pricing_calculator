import requests

# Azure Pricing API URL
API_URL = "https://azure.microsoft.com/api/v3/pricing/storage/calculator/?culture=en-in&discount=mca"

# Function to fetch pricing data
def fetch_pricing_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"[ERROR] Failed to fetch pricing data. Status Code: {response.status_code}")
        return None

# Function to extract user-selectable options dynamically
def extract_options(data):
    return {
        "account_types": {item["slug"]: item["displayName"] for item in data["accountTypes"]},
        "storage_types": {item["slug"]: item["displayName"] for item in data["storageTypes"]},
        "file_structures": {item["slug"]: item["displayName"] for item in data.get("fileStructureTypes", [])},
        "access_tiers": {item["slug"]: item["displayName"] for item in data["accessTypes"]},
        "redundancies": {item["slug"]: item["displayName"] for item in data["redundancies"]},
    }

# Function to get user selection from available options
def get_user_selection(options, prompt):
    print(f"\nAvailable {prompt}: {', '.join(options.keys())}")
    choice = input(f"Enter {prompt.replace('_', ' ')}: ").strip().lower()
    while choice not in options:
        print("[ERROR] Invalid selection. Try again.")
        choice = input(f"Enter {prompt.replace('_', ' ')}: ").strip().lower()
    return choice

# Function to find matching offer keys based on user input
def find_matching_offer(offers, constructed_key):
    for offer in offers.keys():
        if offer.startswith(constructed_key):
            return offer  # Return the first matching offer
    return None  # No match found

# Main Function
def main():
    # Fetch Azure pricing data
    pricing_data = fetch_pricing_data()
    if not pricing_data:
        return

    # Extract available options
    options = extract_options(pricing_data)

    # Get user input dynamically
    account_type = get_user_selection(options["account_types"], "Storage Account Type")
    storage_type = get_user_selection(options["storage_types"], "Storage Type")
    file_structure = get_user_selection(options["file_structures"], "File Structure")
    access_tier = get_user_selection(options["access_tiers"], "Access Tier")
    redundancy = get_user_selection(options["redundancies"], "Redundancy")

    # Construct offer key dynamically
    constructed_key = f"{account_type}-{storage_type}-{file_structure}-{access_tier}-{redundancy}"
    print(f"\n[INFO] Constructed Offer Key: {constructed_key}")

    # Find matching offer key in API response
    matched_offer_key = find_matching_offer(pricing_data["offers"], constructed_key)

    if matched_offer_key:
        print(f"\n[SUCCESS] Matched Offer Key: {matched_offer_key}")
    else:
        print("\n[ERROR] No matching offer key found in Azure Pricing API.")

if __name__ == "__main__":
    main()
