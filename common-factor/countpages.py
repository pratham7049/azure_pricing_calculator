import requests

API_URL = "https://prices.azure.com/api/retail/prices?$filter=serviceName%20eq%20%27Virtual%20Machines%27&armRegionName=eastus&currencyCode=USD"

def count_api_pages(api_url):
    """Fetch all pages from the API and count them."""
    next_page_url = api_url
    page_count = 0

    while next_page_url:
        try:
            response = requests.get(next_page_url, timeout=10)  # 10s timeout
            response.raise_for_status()  # Raise error for bad responses
            
            data = response.json()
            page_count += 1

            next_page_url = data.get("NextPageLink")  # Get next page link
            print(f"Page {page_count} fetched...")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            break  # Exit on failure

    return page_count

if __name__ == "__main__":
    total_pages = count_api_pages(API_URL)
    print(f"\nTotal pages: {total_pages}")
