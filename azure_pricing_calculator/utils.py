def parse_price_data(data):
    """Parse the JSON response and extract the relevant pricing information."""
    if not data or "items" not in data:
        print("Error: No data found.")
        return []
    
    items = []
    for item in data["items"]:
        # Extract relevant fields from each item (can be customized)
        item_info = {
            'productName': item.get('productName', ''),
            'skuName': item.get('skuName', ''),
            'unitPrice': float(item.get('unitPrice', 0)),
            'currencyCode': item.get('currencyCode', ''),
            'meterName': item.get('meterName', ''),
            'description': item.get('description', ''),
        }
        items.append(item_info)
    
    return items
