import requests
import json

# Azure Pricing Categories API URL
CATEGORIES_API_URL = "https://azure.microsoft.com/api/v2/pricing/categories/calculator/?culture=en-in&discount=mca&v=20250219-1155-433953"

def fetch_categories():
    """Fetches Azure pricing categories from the API and structures them dynamically"""
    response = requests.get(CATEGORIES_API_URL)
    
    try:
        data = response.json()
        if not isinstance(data, list):
            print("Unexpected response format")
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
    except Exception as e:
        print(f"Error decoding JSON: {e}")
        return {}

def display_service_families(service_families):
    """Displays all available service families"""
    print("\nAvailable Service Families:\n")
    for index, family in enumerate(service_families.keys(), start=1):
        print(f"{index}. {family}")
    print()

def select_service_family(service_families):
    """Prompts user to select a service family and displays its services"""
    display_service_families(service_families)
    
    try:
        choice = int(input("Select a service family by number: ")) - 1
        family_names = list(service_families.keys())

        if 0 <= choice < len(family_names):
            selected_family = family_names[choice]
            print(f"\nServices under '{selected_family}':\n")
            for service in service_families[selected_family]:
                print(f"- {service['name']}: {service['description']}")
        else:
            print("Invalid selection. Please try again.")
    except ValueError:
        print("Invalid input. Please enter a number.")

def main():
    service_families = fetch_categories()

    if not service_families:
        print("No service families found.")
        return

    select_service_family(service_families)

if __name__ == "__main__":
    main()
