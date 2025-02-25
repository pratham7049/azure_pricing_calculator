from pricing_calculator import display_categories, display_regions, display_vm_skus, display_disk_pricing, display_bandwidth_pricing

def main():
    print("\n===== Azure Pricing Calculator =====")

    # Step 1: Display available categories
    categories = display_categories()
    if not categories:
        print("No categories found.")
        return

    # Allow the user to select a category
    category_choice = int(input("\nSelect a Category by number: "))
    if category_choice < 1 or category_choice > len(categories):
        print("Invalid selection.")
        return

    selected_category = categories[category_choice - 1]
    print(f"\nYou selected: {selected_category}")

    # Step 2: Display available regions for the selected category
    regions = display_regions()
    if not regions:
        print("No regions found.")
        return

    region_choice = int(input("\nSelect a Region by number: "))
    if region_choice < 1 or region_choice > len(regions):
        print("Invalid selection.")
        return

    selected_region = regions[region_choice - 1]
    print(f"\nYou selected: {selected_region}")

    # Step 3: Display relevant service SKUs based on selected category
    if selected_category == "Compute":
        vm_skus = display_vm_skus(selected_region)
        if not vm_skus:
            print("No VM SKUs found.")
            return
        vm_choice = int(input("\nSelect a VM SKU by number: "))
        if vm_choice < 1 or vm_choice > len(vm_skus):
            print("Invalid selection.")
            return
        selected_vm_sku = vm_skus[vm_choice - 1]
        print(f"\nYou selected: {selected_vm_sku}")

    elif selected_category == "Storage":
        disk_types = display_disk_pricing()
        if not disk_types:
            print("No disk types found.")
            return
        disk_choice = int(input("\nSelect a Disk Type by number: "))
        if disk_choice < 1 or disk_choice > len(disk_types):
            print("Invalid selection.")
            return
        selected_disk_type = disk_types[disk_choice - 1]
        print(f"\nYou selected: {selected_disk_type}")

    elif selected_category == "Networking":
        bandwidth_options = display_bandwidth_pricing()
        if not bandwidth_options:
            print("No bandwidth options found.")
            return
        bandwidth_choice = int(input("\nSelect a Bandwidth Option by number: "))
        if bandwidth_choice < 1 or bandwidth_choice > len(bandwidth_options):
            print("Invalid selection.")
            return
        selected_bandwidth = bandwidth_options[bandwidth_choice - 1]
        print(f"\nYou selected: {selected_bandwidth}")

if __name__ == "__main__":
    main()
