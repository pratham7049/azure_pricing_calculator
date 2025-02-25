import requests

# Base URL for all the APIs
BASE_URL = "https://azure.microsoft.com/api/v2"

# Fetch categories (e.g., Compute, Storage, etc.)
def get_categories():
    url = f"{BASE_URL}/pricing/categories/calculator/?culture=en-in&discount=mca&v=20250124-1339-432121"
    return fetch_data(url)

# Fetch available regions for pricing
def get_regions():
    url = f"{BASE_URL}/pricing/calculator/regions/?culture=en-in&v=20250124-1339-432121"
    return fetch_data(url)

# Fetch available currencies
def get_currencies():
    url = f"{BASE_URL}/currencies/?culture=en-in&discount=mca&v=20250124-1339-432121"
    return fetch_data(url)

# Fetch available VM SKUs
def get_vm_skus(region):
    url = f"{BASE_URL}/pricing/virtual-machines/calculator/{region}/?culture=en-in&discount=mca&v=20250124-1339-432121"
    return fetch_data(url)

# Fetch managed disk pricing
def get_disk_pricing():
    url = f"{BASE_URL}/pricing/managed-disks/calculator/?culture=en-in&discount=mca&v=20250124-1339-432121"
    return fetch_data(url)

# Fetch bandwidth pricing
def get_bandwidth_pricing():
    url = f"{BASE_URL}/pricing/bandwidth/calculator/?culture=en-in&discount=mca&v=20250124-1339-432121"
    return fetch_data(url)

# Fetch service configuration
def get_service_config(service):
    url = f"{BASE_URL}/calculator/config/?culture=en-in&discount=mca&v=20250124-1339-432121"
    return fetch_data(url)

# Helper function to make a GET request and handle errors
def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()  # Returns parsed JSON response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
