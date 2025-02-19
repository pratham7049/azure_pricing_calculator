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

# Dynamic input for region, storage type, redundancy, etc.
region = input("Enter region (e.g., eastus): ").strip()
storage_type = input("Enter storage type (e.g., Premium_LRS, Standard_GRS): ").strip()
redundancy = input("Enter redundancy (e.g., Hot, Cool, Archive): ").strip()
capacity_gb = int(input("Enter capacity in GB (e.g., 1000): "))
write_ops = int(input("Enter write operations (e.g., 100000): "))
read_ops = int(input("Enter read operations (e.g., 100000): "))
list_ops = int(input("Enter list operations (e.g., 100000): "))
data_transfer_gb = int(input("Enter data transfer in GB (e.g., 500): "))

# Define API filters for pricing retrieval
# Fetch the pricing for storage
storage_filter = f"serviceName eq 'Storage' and armRegionName eq '{region}' and productName eq '{storage_type}' and skuName eq '{redundancy}'"
# Fetch the pricing for operations (write, read, list)
operations_filter = f"serviceName eq 'Storage' and armRegionName eq '{region}' and (meterName eq 'Write Operations' or meterName eq 'Read Operations' or meterName eq 'List and Create Container Operations')"
# Fetch the pricing for data transfer
data_transfer_filter = f"serviceName eq 'Bandwidth' and armRegionName eq '{region}' and meterName eq 'Data Transfer Out'"

# Fetch pricing data
storage_pricing = get_azure_pricing(storage_filter)
operations_pricing = get_azure_pricing(operations_filter)
data_transfer_pricing = get_azure_pricing(data_transfer_filter)

# Debug: Print fetched data to verify
print("Storage Pricing Data:", storage_pricing)
print("Operations Pricing Data:", operations_pricing)
print("Data Transfer Pricing Data:", data_transfer_pricing)

# Extract relevant prices from the fetched data
storage_cost_per_gb = next((item['unitPrice'] for item in storage_pricing if 'unitPrice' in item), 0)
write_cost_per_10k = next((item['unitPrice'] for item in operations_pricing if 'Write Operations' in item.get('meterName', '')), 0)
read_cost_per_10k = next((item['unitPrice'] for item in operations_pricing if 'Read Operations' in item.get('meterName', '')), 0)
list_cost_per_10k = next((item['unitPrice'] for item in operations_pricing if 'List' in item.get('meterName', '')), 0)
data_transfer_cost_per_gb = next((item['unitPrice'] for item in data_transfer_pricing if 'unitPrice' in item), 0)

# If any of the costs are not found, print a warning and set to zero
if not storage_cost_per_gb:
    print("Warning: No storage cost found.")
if not write_cost_per_10k:
    print("Warning: No write operation cost found.")
if not read_cost_per_10k:
    print("Warning: No read operation cost found.")
if not list_cost_per_10k:
    print("Warning: No list operation cost found.")
if not data_transfer_cost_per_gb:
    print("Warning: No data transfer cost found.")

# Calculate Costs
storage_cost = storage_cost_per_gb * capacity_gb
write_ops_cost = (write_ops / 10000) * write_cost_per_10k
read_ops_cost = (read_ops / 10000) * read_cost_per_10k
list_ops_cost = (list_ops / 10000) * list_cost_per_10k
data_transfer_cost = data_transfer_gb * data_transfer_cost_per_gb
total_cost = storage_cost + write_ops_cost + read_ops_cost + list_ops_cost + data_transfer_cost

# Print Cost Summary
print("\n===== Estimated Monthly Storage Cost =====")
print(f"Region       : {region}")
print(f"Storage Type : {storage_type}")
print(f"Redundancy   : {redundancy}")
print(f"Capacity     : {capacity_gb} GB")
print(f"Storage Cost : ${storage_cost:.2f}")
print(f"Write Ops    : {write_ops} → ${write_ops_cost:.2f}")
print(f"Read Ops     : {read_ops} → ${read_ops_cost:.2f}")
print(f"List Ops     : {list_ops} → ${list_ops_cost:.2f}")
print(f"Data Transfer: {data_transfer_gb} GB → ${data_transfer_cost:.2f}")
print("----------------------------------------")
print(f"Total Cost   : ${total_cost:.2f}")
print("========================================")
