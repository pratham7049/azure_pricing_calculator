import requests
import time

API_URL = "https://prices.azure.com/api/retail/prices?$filter=serviceFamily eq 'Compute'"

def fetch_all_compute_data(api_url, max_pages=100, timeout=10):
    """Fetch all Compute services data with pagination handling."""
    all_data = []
    next_page_url = api_url
    page_count = 0

    while next_page_url and page_count < max_pages:
        try:
            response = requests.get(next_page_url, timeout=timeout)
            response.raise_for_status()  # Raise HTTP errors if any
            data = response.json()

            if 'Items' in data:
                all_data.extend(data['Items'])
            
            next_page_url = data.get('NextPageLink')  # Get next page URL
            page_count += 1
            print(f"Fetched page {page_count}, total services: {len(all_data)}")
            
            time.sleep(1)  # Prevent hitting rate limits
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            break
    
    return all_data

def find_common_factors(data):
    """Find common factors in Compute services based on attributes."""
    attribute_count = {}
    
    for item in data:
        category = item.get("serviceName", "Unknown")
        attribute_count[category] = attribute_count.get(category, 0) + 1
    
    sorted_factors = sorted(attribute_count.items(), key=lambda x: x[1], reverse=True)
    return sorted_factors

def main():
    print("Fetching Compute services data from Azure API...")
    compute_services = fetch_all_compute_data(API_URL)
    
    if compute_services:
        print(f"Total Compute services retrieved: {len(compute_services)}")
        common_factors = find_common_factors(compute_services)
        print("\nCommon Factors in Compute Services:")
        for factor, count in common_factors[:10]:
            print(f"{factor}: {count} occurrences")
    else:
        print("No data retrieved.")

if __name__ == "__main__":
    main()
