import requests
import difflib  

# Function to fetch pricing data from the Azure Pricing API
def fetch_pricing_data():
    url = "https://prices.azure.com/api/retail/prices"
    params = {"currencyCode": "USD", "serviceFamily": "Storage"}  # Fetch only Storage-related pricing

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("Items", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching pricing data: {e}")
        return []

# Function to extract unique values for selection
def get_unique_values(pricing_data, key):
    return sorted(set(item[key] for item in pricing_data if key in item))

# Function to find the closest match
def closest_match(user_input, options):
    matches = difflib.get_close_matches(user_input, options, n=1, cutoff=0.6)
    return matches[0] if matches else None

# Function to prompt user for input with suggestions
def get_user_input(prompt, options, required=True):
    print(f"\nAvailable {prompt} options:")
    for option in options:
        print(f"- {option}")

    while True:
        value = input(f"\nEnter {prompt} (or press Enter to skip): ").strip()

        if not value and not required:  # Allow skipping if not required
            return None

        if value in options:
            return value

        suggestion = closest_match(value, options)
        if suggestion:
            confirm = input(f"Did you mean '{suggestion}'? (Y/N): ").strip().lower()
            if confirm == 'y':
                return suggestion
        
        print(f"Invalid {prompt}! Please select from the list.")

# Function to filter data based on user input
def filter_data(pricing_data, filters):
    filtered_data = pricing_data
    for key, value in filters.items():
        if value:
            filtered_data = [item for item in filtered_data if item.get(key) == value]

    return filtered_data

# Function to calculate total price
def calculate_price(filtered_data, quantity):
    total_price = sum(item['unitPrice'] * quantity for item in filtered_data)
    return total_price

# Main function
def main():
    print("\nFetching latest Azure Storage pricing...\n")
    pricing_data = fetch_pricing_data()

    if not pricing_data:
        print("\nNo pricing data available.")
        return

    # Extract unique Storage Families first (mandatory selection)
    storage_families = get_unique_values(pricing_data, 'serviceFamily')

    if not storage_families:
        print("\nNo storage families found in pricing data.")
        return

    storage_family = get_user_input("Storage Family", storage_families, required=True)

    # Filter data to only include selected Storage Family
    pricing_data = [item for item in pricing_data if item['serviceFamily'] == storage_family]

    # Extract filtered unique values for next selections
    regions = get_unique_values(pricing_data, 'armRegionName')
    skus = get_unique_values(pricing_data, 'skuName')
    meters = get_unique_values(pricing_data, 'meterName')
    products = get_unique_values(pricing_data, 'productName')
    units = get_unique_values(pricing_data, 'unitOfMeasure')

    # Prompt user for selections
    region = get_user_input("Region", regions, required=True)
    sku = get_user_input("SKU", skus, required=True)
    meter = get_user_input("Meter", meters, required=True)
    product = get_user_input("Product", products, required=True)
    unit = get_user_input("Unit of Measure", units, required=True)

    # Filter data based on user choices
    filters = {
        "armRegionName": region,
        "skuName": sku,
        "meterName": meter,
        "productName": product,
        "unitOfMeasure": unit
    }

    filtered_data = filter_data(pricing_data, filters)

    if not filtered_data:
        print("\nNo data found matching your filters.")
        return

    # Get user input for quantity
    try:
        quantity = int(input("\nEnter the quantity of usage (GB, Transactions, etc.): ").strip())
    except ValueError:
        print("Invalid input! Please enter a numeric value.")
        return

    # Calculate total price
    total_price = calculate_price(filtered_data, quantity)

    # Fetch first matching price (assumes all filtered results have similar pricing)
    unit_price = filtered_data[0]['unitPrice']
    currency = filtered_data[0]['currencyCode']

    # ===== Display Cost Summary =====
    print("\n===== Estimated Monthly Storage Cost =====")
    print(f"Region       : {region}")
    print(f"SKU          : {sku}")
    print(f"Meter        : {meter}")
    print(f"Product      : {product}")
    print(f"Unit Measure : {unit}")
    print(f"Unit Price   : {currency} ${unit_price:.4f}")
    print(f"Quantity     : {quantity} {unit}")
    print(f"Total Cost   : {currency} ${total_price:.2f}")
    print("===================================")

if __name__ == "__main__":
    main()
