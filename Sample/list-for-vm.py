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

def list_vm_skus(region):
    """List all available VM SKUs for a given region"""
    url = VM_PRICING_URL.format(region=region)
    data = fetch_data(url)
    
    if not data or "offers" not in data:
        print("Error: Could not retrieve VM SKUs.")
        return []
    
    vm_skus = list(data["offers"].keys())
    
    print("\n===== Available VM SKUs =====")
    for sku in vm_skus:
        print(f"- {sku}")
    
    print(f"\nTotal VM SKUs found: {len(vm_skus)}\n")
    return vm_skus

def list_disk_types():
    """List all available Managed Disk types"""
    data = fetch_data(DISK_PRICING_URL)
    
    if not data or "offers" not in data:
        print("Error: Could not retrieve disk types.")
        return []
    
    disk_types = list(data["offers"].keys())
    
    print("\n===== Available Managed Disk Types =====")
    for disk in disk_types:
        print(f"- {disk}")
    
    print(f"\nTotal Disk Types found: {len(disk_types)}\n")
    return disk_types

def list_bandwidth_options():
    """List all available Bandwidth options"""
    data = fetch_data(BANDWIDTH_PRICING_URL)
    
    if not data or "offers" not in data:
        print("Error: Could not retrieve bandwidth options.")
        return []
    
    bandwidth_options = list(data["offers"].keys())

    print("\n===== Available Bandwidth Options =====")
    for bw in bandwidth_options:
        print(f"- {bw}")
    
    print(f"\nTotal Bandwidth Options found: {len(bandwidth_options)}\n")
    return bandwidth_options

# ===== User Inputs with Listings =====
print("\n===== Azure Pricing Calculator =====")
region = input("Enter Azure region (e.g., us-east, west-europe): ").strip()

# List available VM SKUs before selection
available_vms = list_vm_skus(region)
vm_sku = input("Enter VM SKU from the list above: ").strip()

# List available Disk Types before selection
available_disks = list_disk_types()
disk_type = input("Enter Disk Type from the list above: ").strip()
disk_size = int(input("Enter Disk Size (GB): "))

# List available Bandwidth options before selection
available_bandwidths = list_bandwidth_options()
bandwidth_usage = int(input("Enter Bandwidth Usage (GB): "))

# ===== Cost Calculation =====
def get_vm_cost(region, sku):
    """Retrieve the cost of a Virtual Machine"""
    url = VM_PRICING_URL.format(region=region)
    data = fetch_data(url)
    
    if not data or "offers" not in data:
        print("Error: Could not retrieve VM pricing.")
        return 0
    
    offers = data["offers"]
    if sku in offers:
        price_per_hour = offers[sku]["prices"].get("perhour", {}).get(region, {}).get("value", 0)
        if price_per_hour:
            return float(price_per_hour) * 730  # Convert hourly rate to monthly cost
    print("VM SKU not found or pricing unavailable.")
    return 0

def get_disk_cost(region, disk_type, disk_size):
    """Retrieve the cost of a Managed Disk"""
    data = fetch_data(DISK_PRICING_URL)
    
    if not data or "offers" not in data:
        print("Error: Could not retrieve disk pricing.")
        return 0
    
    for disk_name, disk_info in data["offers"].items():
        if disk_type.lower() in disk_name.lower():
            if "prices" in disk_info and region in disk_info["prices"]:
                price_per_gb = disk_info["prices"][region].get("value", 0)
                if price_per_gb:
                    return float(price_per_gb) * disk_size  # Cost based on selected disk size
    print("Disk type not found or pricing unavailable.")
    return 0

def get_bandwidth_cost(region, bandwidth_usage):
    """Retrieve the cost of Bandwidth usage"""
    data = fetch_data(BANDWIDTH_PRICING_URL)
    
    if not data or "offers" not in data:
        print("Error: Could not retrieve bandwidth pricing.")
        return 0
    
    for bw_name, bw_info in data["offers"].items():
        if "outbound" in bw_name.lower():  # Match outbound bandwidth usage
            if "prices" in bw_info and region in bw_info["prices"]:
                price_per_gb = bw_info["prices"][region].get("value", 0)
                if price_per_gb:
                    return float(price_per_gb) * bandwidth_usage
    print("Bandwidth pricing not found or unavailable.")
    return 0

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
print(f"Total Cost   : ${total_cost:.2f}")
print("===================================")
