import requests

def get_azure_pricing(filter_expression):
    url = "https://prices.azure.com/api/retail/prices"
    params = {"$filter": filter_expression, "$top": 1000}
    prices = []
    
    while url:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print("Error fetching data from Azure Retail API")
            return None
        data = response.json()
        prices.extend(data.get("Items", []))
        url = data.get("NextPageLink")  # Handle pagination
    
    return prices

# User Inputs
print("Please enter the following details:")
region = input("Enter region (e.g., eastus): ").strip()
storage_type = input("Enter storage type (e.g., General Purpose v2, Blob Storage): ").strip()
redundancy = input("Enter redundancy (e.g., LRS, GRS, ZRS, RA-GRS): ").strip()
capacity_gb = int(input("Enter capacity in GB (e.g., 1000): "))

# Operations Input (Multiplied by 10,000)
print("\nEnter the number of operations in multiples of 10,000.")
write_ops_units = int(input("Write Operations (e.g., 1 = 10,000 ops): "))
list_ops_units = int(input("List and Create Container Operations (e.g., 1 = 10,000 ops): "))
read_ops_units = int(input("Read Operations (e.g., 1 = 10,000 ops): "))
other_ops_units = int(input("Other Operations (e.g., 1 = 10,000 ops): "))
data_retrieval_gb = int(input("Enter data retrieval in GB (e.g., 1000): "))

# Multiply by 10,000 as per the image details
write_ops = write_ops_units * 10000
list_ops = list_ops_units * 10000
read_ops = read_ops_units * 10000
other_ops = other_ops_units * 10000

# API Filters
storage_filter = f"serviceName eq 'Storage' and armRegionName eq '{region}' and productName eq '{storage_type}' and skuName eq '{redundancy}'"
operations_filter = f"serviceName eq 'Storage' and armRegionName eq '{region}'"
data_transfer_filter = f"serviceName eq 'Bandwidth' and armRegionName eq '{region}' and meterName eq 'Data Transfer Out'"

# Fetch Pricing Data
storage_pricing = get_azure_pricing(storage_filter)
operations_pricing = get_azure_pricing(operations_filter)
data_transfer_pricing = get_azure_pricing(data_transfer_filter)

# Extract Storage Account Pricing
storage_cost_per_gb = next((item['unitPrice'] for item in storage_pricing if 'unitPrice' in item), 0)

# Operations and Data Transfer Pricing Definitions
write_cost_per_10k = 0.05000  # Write Operations
list_cost_per_10k = 0.05000   # List and Create Container Operations
read_cost_per_10k = 0.00400   # Read Operations
other_cost_per_10k = 0.00400  # All Other Operations
data_retrieval_cost_per_gb = 0.00000  # Data Retrieval (Free)
data_write_cost_per_gb = 0.00000  # Data Write (Free)

# Calculate Costs
storage_cost = storage_cost_per_gb * capacity_gb
write_ops_cost = write_ops_units * write_cost_per_10k
list_ops_cost = list_ops_units * list_cost_per_10k
read_ops_cost = read_ops_units * read_cost_per_10k
other_ops_cost = other_ops_units * other_cost_per_10k
data_retrieval_cost = data_retrieval_gb * data_retrieval_cost_per_gb
data_write_cost = 0  # As per image, data write is free
total_cost = storage_cost + write_ops_cost + list_ops_cost + read_ops_cost + other_ops_cost + data_retrieval_cost + data_write_cost

# Cost Summary with 5 Decimal Places
print("\n===== Estimated Monthly Storage Cost =====")
print(f"Region               : {region}")
print(f"Storage Type         : {storage_type}")
print(f"Redundancy           : {redundancy}")
print(f"Capacity             : {capacity_gb} GB")
print(f"Storage Cost         : ${storage_cost:.5f}")
print(f"Write Ops            : {write_ops} → ${write_ops_cost:.5f}")
print(f"List Ops             : {list_ops} → ${list_ops_cost:.5f}")
print(f"Read Ops             : {read_ops} → ${read_ops_cost:.5f}")
print(f"Other Ops            : {other_ops} → ${other_ops_cost:.5f}")
print(f"Data Retrieval       : {data_retrieval_gb} GB → ${data_retrieval_cost:.5f}")
print(f"Data Write           : 0 (Free)")
print("----------------------------------------")
print(f"Total Cost           : ${total_cost:.5f}")
print("========================================")
