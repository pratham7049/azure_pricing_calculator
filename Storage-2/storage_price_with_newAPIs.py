import requests

# API Endpoints
CATEGORIES_URL = "https://azure.microsoft.com/api/v2/pricing/categories/calculator/?culture=en-in"
REGIONS_URL = "https://azure.microsoft.com/api/v2/pricing/calculator/regions/?culture=en-in"
STORAGE_PRICING_URL = "https://azure.microsoft.com/api/v3/pricing/storage/calculator/?culture=en-in"

def fetch_data(url):
    """Fetch JSON data from API"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def list_categories():
    """List available service categories"""
    data = fetch_data(CATEGORIES_URL)
    if not data or "categories" not in data:
        print("Error: Could not retrieve categories.")
        return []
    
    categories = {cat["id"]: cat["name"] for cat in data["categories"]}
    print("\n===== Available Service Categories =====")
    for cid, cname in categories.items():
        print(f"- {cname} (ID: {cid})")
    return categories

def list_regions():
    """List available Azure regions"""
    data = fetch_data(REGIONS_URL)
    if not data or "regions" not in data:
        print("Error: Could not retrieve regions.")
        return []
    
    regions = {reg["id"]: reg["name"] for reg in data["regions"]}
    print("\n===== Available Azure Regions =====")
    for rid, rname in regions.items():
        print(f"- {rname} (ID: {rid})")
    return regions

def list_storage_skus():
    """List available Storage SKUs"""
    data = fetch_data(STORAGE_PRICING_URL)
    if not data or "offers" not in data:
        print("Error: Could not retrieve storage SKUs.")
        return []
    
    skus = {sku: details["meterName"] for sku, details in data["offers"].items()}
    print("\n===== Available Storage SKUs =====")
    for sku, name in skus.items():
        print(f"- {name} (SKU: {sku})")
    return skus

def get_storage_cost(region, sku, storage_gb, egress_gb):
    """Retrieve the cost of a Storage Account"""
    data = fetch_data(STORAGE_PRICING_URL)
    if not data or "offers" not in data:
        print("Error: Could not retrieve storage pricing.")
        return 0
    
    for storage_name, details in data["offers"].items():
        if sku.lower() in storage_name.lower() and region in details.get("prices", {}):
            price_per_gb = details["prices"][region].get("value", 0)
            return float(price_per_gb) * storage_gb
    print("Storage SKU not found or pricing unavailable.")
    return 0

# ===== User Inputs with Listings =====
print("\n===== Azure Storage Pricing Calculator =====")

# Step 1: List and select category (should include Storage)
categories = list_categories()
storage_category_id = next((cid for cid, cname in categories.items() if "Storage" in cname), None)
if not storage_category_id:
    print("Error: Storage category not found. Exiting.")
    exit()

# Step 2: Select region
regions = list_regions()
if not regions:
    print("Error: No regions found. Exiting.")
    exit()
selected_region = input("Enter Azure region ID from the list above: ").strip()
if selected_region not in regions:
    print("Invalid region selected. Exiting.")
    exit()

# Step 3: Select Storage SKU
storage_skus = list_storage_skus()
selected_sku = input("Enter Storage SKU from the list above: ").strip()
if selected_sku not in storage_skus:
    print("Invalid storage SKU selected. Exiting.")
    exit()

# Step 4: Input storage and egress details
storage_gb = float(input("Enter Storage Capacity (GB): "))
egress_gb = float(input("Enter Data Transfer (Egress) (GB): "))

# ===== Cost Calculation =====
storage_cost = get_storage_cost(selected_region, selected_sku, storage_gb, egress_gb)

total_cost = storage_cost

# ===== Display Cost Summary =====
print("\n===== Estimated Monthly Cost =====")
print(f"Category      : Storage")
print(f"Region       : {regions[selected_region]}")
print(f"Storage SKU  : {storage_skus[selected_sku]}")
print(f"Storage Size : {storage_gb} GB")
print(f"Egress       : {egress_gb} GB")
print(f"Total Cost   : ${total_cost:.2f}")
print("===================================")
