import requests

# Define the API endpoint
API_URL = "https://azure.microsoft.com/api/v2/pricing/categories/calculator/?culture=en-in&discount=mca&v=20250124-1339-432121"

# Function to fetch data from the API
def fetch_data_from_api(api_url):
    print("Fetching data from API...")
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad status codes
        print("Data fetched successfully.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None

# Function to display categories
def display_categories(data):
    if not data:
        print("No data available.")
        return None

    print("\nAvailable Categories:\n")
    categories = {}
    for idx, category in enumerate(data, start=1):
        category_name = category.get("displayName", "Unnamed Category")
        categories[idx] = category
        print(f"{idx}. {category_name}")
    return categories

# Function to display products in a selected category
def display_products(category):
    category_name = category.get("displayName", "Unnamed Category")
    print(f"\nCategory: {category_name}")
    
    products = category.get("products", [])
    if not products:
        print("  No products available in this category.\n")
        return

    print("Products:")
    for product in products:
        product_name = product.get("displayName", "Unnamed Product")
        description = product.get("description", "No description available.")
        pricing_url = product.get("links", {}).get("pricingUrl", "No pricing URL available.")
        
        print(f"  - Product: {product_name}")
        print(f"    Description: {description}")
        print(f"    Pricing URL: {pricing_url}\n")

# Main function to run the interactive menu
def main():
    print("Starting the Azure Pricing Interactive Script...")
    raw_data = fetch_data_from_api(API_URL)
    if not raw_data:
        print("Failed to fetch data from API. Exiting.")
        return
    
    while True:
        print("\nDisplaying categories...")
        categories = display_categories(raw_data)
        if not categories:
            print("No categories to display. Exiting.")
            return

        try:
            choice = int(input("\nEnter the number of the category you want to explore (or 0 to exit): "))
            print(f"You selected: {choice}")
            if choice == 0:
                print("Exiting program. Goodbye!")
                break
            elif choice in categories:
                display_products(categories[choice])
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()
