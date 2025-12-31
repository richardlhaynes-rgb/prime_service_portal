"""
PRIME Service Portal - Inventory Population Script
--------------------------------------------------------------------------------
Purpose:
This script automatically generates "Demo Data" for the Hardware Inventory.
It assigns a standard workstation bundle (Laptop, Dock, 2 Monitors) to every
registered user in the system and creates spare stock items.

Usage:
Run this script from the project root via the Developer Toolkit or command line:
> python populate_inventory.py

Note:
Emojis have been removed from console output to prevent UnicodeEncodeError
on standard Windows command prompts.
--------------------------------------------------------------------------------
"""

import os
import django
import random
from datetime import date, timedelta

# ==============================================================================
# 1. DJANGO ENVIRONMENT SETUP
# ==============================================================================
# We must configure the settings module before we can import models.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import Models (Must happen AFTER django.setup)
from django.contrib.auth.models import User
from inventory.models import AssetCategory, HardwareAsset

# ==============================================================================
# 2. HELPER FUNCTIONS
# ==============================================================================

def get_random_past_date(min_days=30, max_days=730):
    """
    Generates a random date in the past between min_days and max_days ago.
    Used to simulate realistic purchase dates.
    """
    days_ago = random.randint(min_days, max_days)
    purchase_date = date.today() - timedelta(days=days_ago)
    return purchase_date

def get_random_serial(prefix):
    """
    Generates a random 5-digit serial number with a specific prefix.
    Example: SN-LT-48291
    """
    random_digits = random.randint(10000, 99999)
    serial_string = f"{prefix}-{random_digits}"
    return serial_string

# ==============================================================================
# 3. MAIN EXECUTION
# ==============================================================================

def run_heavy_demo():
    """
    Main function to populate the database with assets.
    """
    print("----------------------------------------------------------------")
    print("STARTING: Inventory Population Script")
    print("----------------------------------------------------------------")

    # --------------------------------------------------------------------------
    # Step 1: Validate Categories
    # --------------------------------------------------------------------------
    # We need specific categories to exist for this script to work.
    print("\n[Step 1] Mapping Asset Categories...")
    
    # Create an empty dictionary to store our category objects
    category_map = {}
    
    # Fetch all categories from the database
    all_categories = AssetCategory.objects.all()
    
    # Loop through them and build the map manually
    for cat in all_categories:
        category_map[cat.name] = cat

    # Define the list of required categories we need
    required_categories = [
        'Laptops', 
        'Monitors', 
        'Docking Stations', 
        'Peripherals', 
        'Network Gear'
    ]
    
    # Check if they exist
    for required_cat in required_categories:
        if required_cat not in category_map:
            print(f"CRITICAL ERROR: Missing Category '{required_cat}'")
            print("Please run the Toolkit, go to Database Ops, and click 'Refresh Demo'.")
            return

    print("Categories verified.")

    # --------------------------------------------------------------------------
    # Step 2: Fetch Users
    # --------------------------------------------------------------------------
    print("\n[Step 2] Fetching User List...")
    
    users = list(User.objects.all())
    user_count = len(users)
    
    print(f"Found {user_count} users in the database.")
    print("Preparing to assign workstation bundles (Laptop + Dock + 2 Monitors) to each.")

    # Counter to keep asset tags unique during this run
    global_asset_counter = 100

    # --------------------------------------------------------------------------
    # Step 3: Create User Workstations
    # --------------------------------------------------------------------------
    print("\n[Step 3] Creating Assigned Assets...")

    for user in users:
        print(f"   -> Provisioning for user: {user.username}")

        # --- A. Create Laptop ---
        laptop_models = ['Precision 5680', 'MacBook Pro M3', 'ThinkPad P1']
        laptop_manufacturers = ['Dell', 'Apple', 'Lenovo']
        
        # Pick random model/manufacturer (simplified logic: pick same index for realism)
        choice_index = random.randint(0, 2)
        selected_model = laptop_models[choice_index]
        selected_mfg = laptop_manufacturers[choice_index]

        HardwareAsset.objects.create(
            asset_tag=f"PRIME-LT-{global_asset_counter}",
            serial_number=get_random_serial("SN-LT"),
            category=category_map['Laptops'],
            manufacturer=selected_mfg,
            model_number=selected_model,
            assigned_to=user,
            status='deployed',
            purchase_date=get_random_past_date()
        )
        global_asset_counter += 1

        # --- B. Create Docking Station ---
        HardwareAsset.objects.create(
            asset_tag=f"PRIME-DK-{global_asset_counter}",
            serial_number=get_random_serial("SN-DK"),
            category=category_map['Docking Stations'],
            manufacturer='Dell',
            model_number='WD22TB4 Thunderbolt',
            assigned_to=user,
            status='deployed',
            purchase_date=get_random_past_date()
        )
        global_asset_counter += 1

        # --- C. Create Dual Monitors (Loop twice) ---
        for i in range(2):
            HardwareAsset.objects.create(
                asset_tag=f"PRIME-MN-{global_asset_counter}",
                serial_number=get_random_serial("SN-MN"),
                category=category_map['Monitors'],
                manufacturer='Dell',
                model_number='UltraSharp 27 Inch',
                assigned_to=user,
                status='deployed',
                purchase_date=get_random_past_date()
            )
            global_asset_counter += 1

    # --------------------------------------------------------------------------
    # Step 4: Create Unassigned Stock (Spare Parts)
    # --------------------------------------------------------------------------
    print("\n[Step 4] creating Spare Inventory...")

    # Define the stock we want to create
    # Format: (Category Name, Status, Count to create)
    stock_requirements = [
        ('Laptops', 'available', 5),
        ('Laptops', 'maintenance', 3),
        ('Laptops', 'retired', 3),
        ('Monitors', 'available', 5),
        ('Network Gear', 'available', 4),
    ]

    for cat_name, status, count in stock_requirements:
        
        # Loop 'count' times to create the items
        for i in range(count):
            
            # Determine logic based on category
            if cat_name == 'Network Gear':
                mfg = 'Ubiquiti'
                model = 'Dream Machine Pro'
            else:
                mfg = 'Dell'
                model = 'Spare Inventory Item'

            HardwareAsset.objects.create(
                asset_tag=f"PRIME-STK-{global_asset_counter}",
                serial_number=get_random_serial("SN-STK"),
                category=category_map[cat_name],
                manufacturer=mfg,
                model_number=model,
                assigned_to=None, # Explicitly unassigned
                status=status,
                purchase_date=get_random_past_date(min_days=400, max_days=1000)
            )
            global_asset_counter += 1
            
        print(f"   -> Created {count} items in category '{cat_name}' with status '{status}'")

    # --------------------------------------------------------------------------
    # Step 5: Final Summary
    # --------------------------------------------------------------------------
    total_assets = HardwareAsset.objects.count()
    
    print("\n----------------------------------------------------------------")
    print("SUCCESS: Database Population Complete")
    print(f"Total Assets in Database: {total_assets}")
    print("----------------------------------------------------------------")

if __name__ == '__main__':
    run_heavy_demo()