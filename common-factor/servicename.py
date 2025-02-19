import requests
import time
from collections import Counter

API_URL = "https://prices.azure.com/api/retail/prices?$filter=serviceFamily%20eq%20%27Compute%27"
MAX_PAGES = 100  # Safety limit to avoid infinite loops

def fetch_all_compute_data(api_url):
    """Fetch all Compute service data from the Azure API with pagination handling."""
    all_services = []
    next_page_url = api_url
    page_count = 0

    while next_page_url and page_count < MAX_PAGES:
        try:
            response = requests.get(next_page_url, timeout=10)  # 10s timeout
            response.raise_for_status()  # Raise error for bad responses

            data = response.json()
            all_services.extend(data.get("Items", []))

            next_page_url = data.get("NextPageLink")  # Get next page link
            page_count += 1  # Track pages processed

            if next_page_url:
                print(f"Fetching next page... ({page_count})")
                time.sleep(1)  # Avoid hitting rate limits

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            break  # Exit loop on error

    return all_services

def extract_common_factors(services):
    """Extract the most common service names from the fetched data."""
    service_names = [service.get("serviceName", "Unknown") for service in services]
    service_counts = Counter(service_names)

    print("\nMost Common Compute Services:")
    for service, count in service_counts.most_common(10):  # Display top 10
        print(f"{service}: {count} occurrences")

def main():
    print("Fetching Compute services data from Azure API...\n")
    compute_services = fetch_all_compute_data(API_URL)

    if compute_services:
        print(f"\nTotal Compute services retrieved: {len(compute_services)}")
        extract_common_factors(compute_services)
    else:
        print("No Compute services found.")

if __name__ == "__main__":
    main()
