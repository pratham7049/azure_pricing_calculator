import requests

# API Endpoints
VM_PRICING_URL = "https://azure.microsoft.com/api/v4/pricing/virtual-machines/calculator/{region}/?culture=en-in"
DISK_PRICING_URL = "https://azure.microsoft.com/api/v2/pricing/managed-disks/calculator/?culture=en-in"
BANDWIDTH_PRICING_URL = "https://azure.microsoft.com/api/v2/pricing/bandwidth/calculator/?culture=en-in"

def fetch_data(url):
    """Fetch JSON data from API"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def list_vm_series(region):
    """List all available VM series for a given region"""
    url = VM_PRICING_URL.format(region=region)
    data = fetch_data(url)
    
    if not data or "offers" not in data:
        print("Error: Could not retrieve VM series.")
        return []
    
    vm_series = sorted(set(sku.split('_')[0] for sku in data["offers"].keys()))
    print("\n===== Available VM Series =====")
    for series in vm_series:
        print(f"- {series}")
    
    return vm_series

def list_vm_skus(region, selected_series):
    """List all available VM SKUs for a selected series and region"""
    url = VM_PRICING_URL.format(region=region)
    data = fetch_data(url)
    
    if not data or "offers" not in data:
        print("Error: Could not retrieve VM SKUs.")
        return []
    
    vm_skus = [sku for sku in data["offers"].keys() if sku.startswith(selected_series)]
    
    print("\n===== Available VM SKUs =====")
    for sku in vm_skus:
        print(f"- {sku}")
    
    return vm_skus

def get_vm_cost(region, sku):
    """Retrieve the cost of a Virtual Machine"""
    url = VM_PRICING_URL.format(region=region)
    data = fetch_data(url)
    
    if not data or "offers" not in data:
        print("Error: Could not retrieve VM pricing.")
        return 0
    
    if sku in data["offers"]:
        price_per_hour = data["offers"][sku].get("prices", {}).get("perhour", {}).get(region, {}).get("value", 0)
        return float(price_per_hour) * 730
    
    print("VM SKU not found or pricing unavailable.")
    return 0

def list_disk_types():
    """List all available Managed Disk types"""
    data = fetch_data(DISK_PRICING_URL)
    
    if not data or "offers" not in data:
        print("Error: Could not retrieve disk types.")
        return []
    
    disk_types = sorted(data["offers"].keys())
    print("\n===== Available Managed Disk Types =====")
    for disk in disk_types:
        print(f"- {disk}")
    
    return disk_types

def get_disk_cost(region, disk_type, disk_size):
    """Retrieve the cost of a Managed Disk"""
    data = fetch_data(DISK_PRICING_URL)
    
    if not data or "offers" not in data:
        print("Error: Could not retrieve disk pricing.")
        return 0
    
    if disk_type in data["offers"]:
        price_per_gb = data["offers"][disk_type]["prices"].get(region, {}).get("value", 0)
        return float(price_per_gb) * disk_size
    
    print("Disk type not found or pricing unavailable.")
    return 0

def get_bandwidth_cost(region, bandwidth_usage):
    """Retrieve the cost of Bandwidth usage"""
    data = fetch_data(BANDWIDTH_PRICING_URL)
    
    if not data or "offers" not in data:
        print("Error: Could not retrieve bandwidth pricing.")
        return 0
    
    for bw_info in data["offers"].values():
        if "prices" in bw_info and region in bw_info["prices"]:
            price_per_gb = bw_info["prices"][region].get("value", 0)
            return float(price_per_gb) * bandwidth_usage
    
    print("Bandwidth pricing not found or unavailable.")
    return 0

# ===== User Inputs with Listings =====
print("\n===== Azure Pricing Calculator =====")
region = input("Enter Azure region (e.g., us-east, west-europe): ").strip()

# Select VM series
available_series = list_vm_series(region)
selected_series = input("Select a VM Series from the list above: ").strip()

# Select VM SKU
available_vms = list_vm_skus(region, selected_series)
vm_sku = input("Enter VM SKU from the list above: ").strip()

# Select Disk Type
available_disks = list_disk_types()
disk_type = input("Enter Disk Type from the list above: ").strip()
disk_size = int(input("Enter Disk Size (GB): "))

# Enter Bandwidth Usage
bandwidth_usage = int(input("Enter Bandwidth Usage (GB): "))

# ===== Cost Calculation =====
vm_cost = get_vm_cost(region, vm_sku)
disk_cost = get_disk_cost(region, disk_type, disk_size)
bandwidth_cost = get_bandwidth_cost(region, bandwidth_usage)
total_cost = vm_cost + disk_cost + bandwidth_cost

# ===== Display Cost Summary =====
print("\n===== Estimated Monthly Cost =====")
print(f"Region       : {region}")
print(f"VM SKU       : {vm_sku}")
print(f"Disk Type    : {disk_type}")
print(f"Disk Size    : {disk_size} GB")
print(f"Bandwidth    : {bandwidth_usage} GB")
print(f"VM Cost      : ${vm_cost:.2f}")
print(f"Disk Cost    : ${disk_cost:.2f}")
print(f"Bandwidth Cost : ${bandwidth_cost:.2f}")
print(f"Total Cost   : ${total_cost:.2f}")
print("===================================")
