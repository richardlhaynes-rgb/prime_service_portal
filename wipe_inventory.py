"""
PRIME Service Portal - Inventory Wipe Script
--------------------------------------------------------------------------------
Purpose:
This script performs a hard delete of ALL hardware assets in the database.
It is designed to reset the inventory to a clean slate while preserving
the underlying Asset Categories.

Usage:
Run this script via the Developer Toolkit's "Wipe Inventory DB" button.

WARNING:
This script does NOT ask for confirmation when run. It assumes the calling
application (The Toolkit) has already handled the "Are you sure?" check.
--------------------------------------------------------------------------------
"""

import os
import django

# ==============================================================================
# 1. DJANGO ENVIRONMENT SETUP
# ==============================================================================
# Configure the settings module so we can access the database
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import Models (Must be done after django.setup())
from inventory.models import HardwareAsset

# ==============================================================================
# 2. MAIN EXECUTION
# ==============================================================================

def wipe_demo_data():
    """
    Main function to clear the hardware inventory table.
    """
    print("----------------------------------------------------------------")
    print("STARTING: Inventory Wipe Protocol")
    print("----------------------------------------------------------------")

    # --------------------------------------------------------------------------
    # Step 1: Analyze Current Data
    # --------------------------------------------------------------------------
    # Count how many records exist before we delete them
    asset_count = HardwareAsset.objects.count()
    
    print(f"Scanning database...")
    print(f"Found {asset_count} assets currently in the system.")

    # If the database is already empty, we can stop here.
    if asset_count == 0:
        print("\n[Result] No assets found to delete. Database is already clean.")
        print("----------------------------------------------------------------")
        return

    # --------------------------------------------------------------------------
    # Step 2: Perform Deletion
    # --------------------------------------------------------------------------
    # NOTE: The Toolkit UI has already asked the user for confirmation.
    # We proceed immediately to delete the records.
    print(f"\n[Action] Deleting {asset_count} records...")
    
    # The .all().delete() method is the most efficient way to wipe the table
    # It returns a tuple containing the number of deleted objects
    deleted_info = HardwareAsset.objects.all().delete()
    
    # --------------------------------------------------------------------------
    # Step 3: Final Report
    # --------------------------------------------------------------------------
    print("\n----------------------------------------------------------------")
    print("SUCCESS: Inventory Wiped")
    print(f"Records Removed: {deleted_info[0]}")
    print("Categories have been preserved.")
    print("----------------------------------------------------------------")

if __name__ == '__main__':
    wipe_demo_data()