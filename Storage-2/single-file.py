import requests
import json

# Azure Pricing API URLs
CATEGORIES_API_URL = "https://azure.microsoft.com/api/v2/pricing/categories/calculator/?culture=en-in&discount=mca&v=20250219-1155-433953"
REGIONS_API_URL = "https://azure.microsoft.com/api/v2/pricing/calculator/regions/?culture=en-in"

def fetch_data(url):
    """Fetches JSON data from the given API URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def fetch_categories():
    """Fetches Azure pricing categories and organizes them into service families."""
    data = fetch_data(CATEGORIES_API_URL)
    if not data or not isinstance(data, list):
        print("Unexpected response format from categories API.")
        return {}

    service_families = {}
    for category in data:
        family_name = category.get("displayName", "Uncategorized")
        products = category.get("products", [])

        if family_name not in service_families:
            service_families[family_name] = []

        for product in products:
            service_families[family_name].append({
                "slug": product.get("slug"),
                "name": product.get("displayName"),
                "description": product.get("description")
            })

    return service_families

def fetch_regions():
    """Fetches and returns available Azure regions."""
    data = fetch_data(REGIONS_API_URL)
    if not data or "regions" not in data:
        print("Failed to fetch regions.")
        return {}

    return {r["slug"]: r["displayName"] for r in data["regions"]}

def display_service_families(service_families):
    """Displays all available service families."""
    print("\nAvailable Service Families:\n")
    sorted_families = sorted(service_families.keys())  # Sorting alphabetically
    for index, family in enumerate(sorted_families, start=1):
        print(f"{index}. {family}")
    return sorted_families

def select_service_family(service_families):
    """Prompts user to select a service family and returns the selected family."""
    sorted_families = display_service_families(service_families)
    
    while True:
        try:
            choice = int(input("Select a service family by number: ")) - 1
            if 0 <= choice < len(sorted_families):
                return sorted_families[choice]
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def display_services(services):
    """Displays all services under a selected service family."""
    print("\nAvailable Services:\n")
    sorted_services = sorted(services, key=lambda s: s["name"])
    for index, service in enumerate(sorted_services, start=1):
        print(f"{index}. {service['name']} - {service['description']}")
    return sorted_services

def select_service(services):
    """Prompts user to select a service and returns the selected service."""
    sorted_services = display_services(services)
    
    while True:
        try:
            choice = int(input("Select a service by number: ")) - 1
            if 0 <= choice < len(sorted_services):
                return sorted_services[choice]
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def display_regions(regions):
    """Displays available Azure regions."""
    print("\nAvailable Regions:\n")
    sorted_regions = sorted(regions.items(), key=lambda x: x[1])
    for index, (slug, name) in enumerate(sorted_regions, start=1):
        print(f"{index}. {name}")
    return sorted_regions

def select_region(regions):
    """Prompts user to select a region and returns the selected region."""
    sorted_regions = display_regions(regions)
    
    while True:
        try:
            choice = int(input("Select a region by number: ")) - 1
            if 0 <= choice < len(sorted_regions):
                return sorted_regions[choice][0]  # Return slug
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    """Main function that drives the selection process."""
    service_families = fetch_categories()
    if not service_families:
        print("No service families found.")
        return

    selected_family = select_service_family(service_families)
    services = service_families[selected_family]

    selected_service = select_service(services)
    
    regions = fetch_regions()
    if not regions:
        return
    
    selected_region = select_region(regions)

    # Display final selections
    print("\nYour Final Selections:")
    print(f"Service Family: {selected_family}")
    print(f"Service: {selected_service['name']}")
    print(f"Region: {regions[selected_region]}")

if __name__ == "__main__":
    main()
