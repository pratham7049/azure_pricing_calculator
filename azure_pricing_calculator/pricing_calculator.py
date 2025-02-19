from api_handler import get_categories, get_regions, get_vm_skus, get_disk_pricing, get_bandwidth_pricing

def display_categories():
    """Display available service categories."""
    categories = get_categories()
    if categories:
        print("Available Categories:")
        for idx, category in enumerate(categories.get('items', []), start=1):
            print(f"{idx}. {category['categoryName']}")
        return [category['categoryName'] for category in categories.get('items', [])]
    return []

def display_regions():
    """Display available regions."""
    regions = get_regions()
    if regions:
        print("Available Regions:")
        for idx, region in enumerate(regions.get('items', []), start=1):
            print(f"{idx}. {region['name']}")
        return [region['name'] for region in regions.get('items', [])]
    return []

def display_vm_skus(region):
    """Display available Virtual Machine SKUs."""
    vm_skus = get_vm_skus(region)
    if vm_skus:
        print("Available VM SKUs:")
        for idx, sku in enumerate(vm_skus.get('items', []), start=1):
            print(f"{idx}. {sku['skuName']}")
        return [sku['skuName'] for sku in vm_skus.get('items', [])]
    return []

def display_disk_pricing():
    """Display available Disk Pricing."""
    disk_pricing = get_disk_pricing()
    if disk_pricing:
        print("Available Disk Types:")
        for idx, disk in enumerate(disk_pricing.get('items', []), start=1):
            print(f"{idx}. {disk['name']}")
        return [disk['name'] for disk in disk_pricing.get('items', [])]
    return []

def display_bandwidth_pricing():
    """Display available Bandwidth Pricing."""
    bandwidth_pricing = get_bandwidth_pricing()
    if bandwidth_pricing:
        print("Available Bandwidth Options:")
        for idx, bandwidth in enumerate(bandwidth_pricing.get('items', []), start=1):
            print(f"{idx}. {bandwidth['name']}")
        return [bandwidth['name'] for bandwidth in bandwidth_pricing.get('items', [])]
    return []
