import sys
import time
import random
import datetime
import os
from django.db import connection
from django.contrib.auth import get_user_model
from django.utils import timezone

# -------------------------------------------------------------------------
# 1. APP CONFIGURATION
# -------------------------------------------------------------------------
# Ensure 'inventory' matches your Django App name
from inventory.models import Asset, Category

User = get_user_model()

# Target inventory size
TARGET_TOTAL = 325 
START_DATE_RANGE = datetime.date(2022, 1, 1)

# -------------------------------------------------------------------------
# 2. VISUALS & UTILS
# -------------------------------------------------------------------------
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def progress_bar(current, total, prefix='', length=40):
    percent = float(current) * 100 / total
    arrow = '█' * int(percent/100 * length - 1)
    spaces = '░' * (length - len(arrow))
    sys.stdout.write(f"\r{prefix} |{Colors.BLUE}{arrow}{spaces}{Colors.ENDC}| {int(percent)}% ({current}/{total})")
    sys.stdout.flush()

# -------------------------------------------------------------------------
# 3. SAFETY PROTOCOLS
# -------------------------------------------------------------------------
def check_safety_interlock():
    """
    Checks for the 'PRIME_FORCE_MODE' environment variable. 
    If found, skips confirmation (assumes Batch file handled it).
    """
    if os.environ.get('PRIME_FORCE_MODE') == '1':
        print(f"{Colors.GREEN}[ SYSTEM OVERRIDE ACCEPTED ]{Colors.ENDC} Batch Protocol Detected.")
        return

    current_count = Asset.objects.count()
    print(f"\n{Colors.RED}{Colors.BOLD}!!! MANUAL OVERRIDE DETECTED !!!{Colors.ENDC}")
    print(f"You are running this script directly. It will wipe {Colors.YELLOW}{current_count}{Colors.ENDC} assets.")
    print(f"Type {Colors.BOLD}'DESTROY'{Colors.ENDC} to confirm:")
    
    # Logic for manual running (not via batch)
    if sys.stdin.isatty():
        choice = input(f"{Colors.RED}> {Colors.ENDC}")
        if choice != 'DESTROY':
            sys.exit("Aborted.")
    else:
        time.sleep(5)

# -------------------------------------------------------------------------
# 4. RICH DATA DATASETS
# -------------------------------------------------------------------------

# (Manufacturer, Model, Cost Low, Cost High)
MODELS_DB = {
    'Laptops': [
        ('Dell', 'Precision 5680 Mobile Workstation', 2400, 3200),
        ('Dell', 'Latitude 7440 Ultralight', 1600, 2100),
        ('Dell', 'XPS 15 9530', 1800, 2500),
        ('HP', 'ZBook Firefly 16 G10', 1900, 2600),
        ('HP', 'EliteBook 840 G10', 1400, 1900),
        ('Lenovo', 'ThinkPad X1 Carbon Gen 11', 1700, 2300),
        ('Microsoft', 'Surface Laptop Studio 2', 2200, 2900)
    ],
    'Smartphones': [
        ('Apple', 'iPhone 15 Pro Max', 1199, 1599),
        ('Apple', 'iPhone 15 Pro', 999, 1299),
        ('Apple', 'iPhone 14', 799, 999),
        ('Apple', 'iPhone SE (3rd Gen)', 429, 579),
        ('Samsung', 'Galaxy S24 Ultra', 1299, 1619),
        ('Samsung', 'Galaxy S23+', 999, 1199)
    ],
    'Tablets': [
        ('Apple', 'iPad Pro 12.9" (M2)', 1099, 1499),
        ('Apple', 'iPad Air 5th Gen', 599, 749),
        ('Samsung', 'Galaxy Tab S9 Ultra', 1199, 1399)
    ],
    'Mobile Hotspots': [
        ('Inseego', 'MiFi X PRO 5G', 300, 400),
        ('Netgear', 'Nighthawk M6 Pro', 450, 500),
        ('Franklin', 'JEXtream 5G', 250, 300)
    ],
    'Monitors': [
        ('Dell', 'UltraSharp U2724D', 350, 450),
        ('Dell', 'P2422H', 180, 220),
        ('HP', 'E27 G5 FHD', 250, 300),
        ('LG', '27UK850-W 4K', 400, 500)
    ],
    'Docking Stations': [
        ('Dell', 'WD19S 180W', 220, 280),
        ('Dell', 'WD22TB4 Thunderbolt 4', 320, 380),
        ('HP', 'Thunderbolt Dock G4', 280, 340),
        ('Kensington', 'SD5700T', 250, 300)
    ],
    'Network Infrastructure': [
        ('Cisco', 'Catalyst 9200L 48-Port', 3500, 4500),
        ('Cisco', 'Meraki MX68 Firewall', 900, 1400),
        ('Ubiquiti', 'Dream Machine Pro SE', 499, 499),
        ('Ubiquiti', 'Switch Pro 48 PoE', 1099, 1099)
    ]
}

# Specs
CPU_POOLS = ['Intel Core i7-1365U', 'Intel Core i9-13900H', 'Intel Core i5-1335U', 'AMD Ryzen 7 PRO 7840U', 'Apple M2 Pro', 'Apple M3 Max']
GPU_POOLS = ['NVIDIA RTX 2000 Ada', 'NVIDIA RTX 4050 Laptop', 'Intel Iris Xe', 'Integrated UHD', 'NVIDIA RTX 3050 Ti']
OS_POOLS = {
    'Laptop': ['Windows 11 Pro', 'Windows 11 Enterprise', 'Windows 10 Enterprise'],
    'Phone': ['iOS 17.2', 'iOS 16.6', 'Android 14 (One UI 6.0)', 'Android 13'],
    'Tablet': ['iPadOS 17.1', 'iPadOS 16.5', 'Android 13']
}

# Real Vendor MAC OUIs (Prefixes)
MAC_OUI = {
    'Dell': '00:14:22', 'HP': 'FC:15:B4', 'Apple': '00:1C:B3',
    'Cisco': '00:00:0C', 'Samsung': '00:16:32', 'Ubiquiti': 'B4:FB:E4'
}

# Mobile Data
CARRIERS = ['Verizon Wireless', 'AT&T Business', 'T-Mobile Enterprise', 'FirstNet']
PLANS = ['Unlimited Enterprise Plus', 'Business Data 50GB', 'Pooled Corporate Plan', 'Gov/Ed Unlimited']

# -------------------------------------------------------------------------
# 5. GENERATOR ENGINE
# -------------------------------------------------------------------------

class AssetGenerator:
    def __init__(self):
        self.tag_counters = {
            'LT': 1000, 'DT': 1000, 'PH': 2000, 'TB': 3000,
            'HS': 4000, 'MN': 5000, 'DK': 6000, 'NET': 8000, 'GEN': 9000
        }

    def _get_next_tag(self, category_name):
        prefix_map = {
            'Laptops': 'LT', 'Desktops': 'DT', 'Smartphones': 'PH',
            'Tablets': 'TB', 'Mobile Hotspots': 'HS', 'Monitors': 'MN',
            'Docking Stations': 'DK', 'Network Infrastructure': 'NET'
        }
        prefix = prefix_map.get(category_name, 'GEN')
        self.tag_counters[prefix] += random.randint(1, 3) # Skip a few for realism
        return f"PRIME-{prefix}-{self.tag_counters[prefix]}"

    def _generate_serial(self, manufacturer):
        """Generates serial formats based on manufacturer patterns."""
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        if manufacturer == 'Dell':
            return "".join(random.choices(chars, k=7))
        elif manufacturer == 'HP':
            return "5CG" + "".join(random.choices("0123456789", k=7))
        elif manufacturer == 'Apple':
            return "".join(random.choices(chars, k=10))
        elif manufacturer == 'Cisco':
            return "FDO" + "".join(random.choices("0123456789", k=8))
        else:
            return "".join(random.choices(chars, k=12))

    def _generate_mac(self, manufacturer):
        prefix = MAC_OUI.get(manufacturer, "00:50:56") 
        suffix = ":".join(["%02x" % random.randint(0, 255) for _ in range(3)]).upper()
        return f"{prefix}:{suffix}"

    def _generate_history_notes(self):
        events = [
            f"[{datetime.date(2023, random.randint(1,12), random.randint(1,28))}] Device imaged and deployed.",
            f"[{datetime.date(2024, random.randint(1,5), random.randint(1,28))}] User reported sluggishness. Cleaned temp files.",
            "Asset tag re-applied due to peeling.",
            "Missing original box.",
            "Assigned to remote user pool.",
            "Upgraded RAM to 32GB on request."
        ]
        if random.random() > 0.4:
            return "\n".join(random.sample(events, k=random.randint(1, 3)))
        return ""

    def create_asset(self, category, assigned_user=None, force_status=None):
        # 1. Selection
        model_data = MODELS_DB.get(category.name, MODELS_DB['Laptops'])
        manuf, model, cost_min, cost_max = random.choice(model_data)
        
        # 2. Status Logic
        if force_status:
            status = force_status
        else:
            status = random.choices(
                ['In Stock', 'Maintenance', 'Retired'], 
                weights=[85, 10, 5], k=1
            )[0]
        if assigned_user: status = 'Deployed'

        # 3. Dates
        today = datetime.date.today()
        purchase_date = START_DATE_RANGE + datetime.timedelta(days=random.randint(0, 700))
        warranty_date = purchase_date + datetime.timedelta(days=365*3)

        # 4. JSON Specs Building
        specs = {}
        
        # --- A. SYSTEM CONFIG ---
        if category.name in ['Laptops', 'Desktops', 'Workstations', 'Tablets']:
            specs['hostname'] = f"CORP-{manuf[:3].upper()}-{random.randint(100,999)}"
            specs['cpu'] = random.choice(CPU_POOLS)
            specs['ram'] = random.choice(['16 GB', '32 GB', '64 GB'])
            specs['gpu'] = random.choice(GPU_POOLS)
            specs['storage'] = random.choice(['512 GB SSD', '1 TB NVMe'])
            
            if category.name == 'Tablets':
                specs['os'] = random.choice(OS_POOLS['Tablet'])
                specs['gpu'] = "Integrated Apple GPU" if manuf == 'Apple' else "Adreno"
            else:
                specs['os'] = random.choice(OS_POOLS['Laptop'])

        # --- B. SMARTPHONE SPECIFIC ---
        elif category.name == 'Smartphones':
            specs['os'] = random.choice(OS_POOLS['Phone'])
            specs['storage'] = random.choice(['128 GB', '256 GB', '512 GB'])
            # Clear others
            specs['hostname'] = ""
            specs['cpu'] = "" 
            specs['ram'] = ""

        # --- C. MOBILE BROADBAND ---
        if category.name in ['Smartphones', 'Tablets', 'Mobile Hotspots']:
            specs['mob_enabled'] = True
            specs['mob_carrier'] = random.choice(CARRIERS)
            specs['mob_phone'] = f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}"
            specs['mob_plan'] = random.choice(PLANS)
            specs['mob_imei'] = "".join([str(random.randint(0,9)) for _ in range(15)])
            specs['mob_iccid'] = "8901" + "".join([str(random.randint(0,9)) for _ in range(16)])
            specs['mob_account'] = f"VZW-{random.randint(800000, 999999)}"
            specs['mob_contract'] = str(warranty_date)
            specs['mob_status'] = "Active" if status == 'Deployed' else "Suspended"
        else:
            specs['mob_enabled'] = False

        # --- D. NETWORK CONFIG ---
        if category.name in ['Laptops', 'Desktops', 'Network Infrastructure']:
            specs['net_mac'] = self._generate_mac(manuf)
            
            if category.name == 'Network Infrastructure':
                specs['net_assignment'] = "Manual"
                specs['net_ipv4'] = f"10.50.10.{random.randint(2, 250)}"
                specs['net_vlan'] = "10 (Management)"
                specs['net_desc'] = "Uplink to Core"
                specs['net_port'] = "Trunk"
            else:
                specs['net_assignment'] = "DHCP"
                specs['net_desc'] = "Primary LAN"
                specs['net_port'] = f"Gi1/0/{random.randint(1,48)}"

        # 5. Create Record
        Asset.objects.create(
            asset_tag=self._get_next_tag(category.name),
            serial_number=self._generate_serial(manuf),
            manufacturer=manuf,
            model_number=model,
            category=category,
            status=status,
            assigned_to=assigned_user,
            vendor=random.choice(['CDW-G', 'Insight', 'SHI', 'Direct']),
            purchase_date=purchase_date,
            warranty_expiration=warranty_date,
            cost=random.randint(cost_min, cost_max),
            specs=specs,
            support_notes=f"Standard {manuf} ProSupport. Expires {warranty_date.strftime('%m/%Y')}.",
            notes=self._generate_history_notes()
        )

# -------------------------------------------------------------------------
# 5. ORCHESTRATION
# -------------------------------------------------------------------------

def run_seed():
    # 1. SAFETY CHECK
    check_safety_interlock()
    
    print("\n" + "="*60)
    print(f"   PRIME ASSET ORCHESTRATOR (v5.0 Enterprise)")
    print("="*60 + "\n")
    
    # 2. PURGE
    print(f"{Colors.CYAN}[1/4] Wiping Database...{Colors.ENDC}")
    with connection.cursor() as cursor:
        cursor.execute(f"TRUNCATE TABLE {Asset._meta.db_table} RESTART IDENTITY CASCADE;")
    print(f"{Colors.GREEN}      ✔ Database Cleaned.{Colors.ENDC}")

    # 3. CATEGORIES
    print(f"\n{Colors.CYAN}[2/4] Verifying Category Taxonomy...{Colors.ENDC}")
    required_cats = [
        'Laptops', 'Desktops', 'Smartphones', 'Tablets', 
        'Mobile Hotspots', 'Monitors', 'Docking Stations', 
        'Network Infrastructure'
    ]
    categories = {}
    for name in required_cats:
        cat, _ = Category.objects.get_or_create(name=name)
        categories[name] = cat
    print(f"{Colors.GREEN}      ✔ {len(categories)} Categories Loaded.{Colors.ENDC}")

    # 4. STANDARD KIT ASSIGNMENT
    users = list(User.objects.all())
    print(f"\n{Colors.CYAN}[3/4] Deploying Standard Kits to {len(users)} Users...{Colors.ENDC}")
    
    generator = AssetGenerator()
    assets_created_count = 0
    
    for i, user in enumerate(users):
        generator.create_asset(categories['Smartphones'], user)
        generator.create_asset(categories['Mobile Hotspots'], user)
        generator.create_asset(categories['Laptops'], user)
        generator.create_asset(categories['Docking Stations'], user)
        generator.create_asset(categories['Monitors'], user)
        generator.create_asset(categories['Monitors'], user)
        
        assets_created_count += 6
        progress_bar(i + 1, len(users), prefix="      Deployment Progress")

    print(f"\n{Colors.GREEN}      ✔ All users equipped. ({assets_created_count} assets created){Colors.ENDC}")

    # 5. FILLER INVENTORY
    remaining = TARGET_TOTAL - assets_created_count
    if remaining > 0:
        print(f"\n{Colors.CYAN}[4/4] Stocking Warehouse with {remaining} Spare Assets...{Colors.ENDC}")
        
        for i in range(remaining):
            cat_choice = random.choices(
                ['Laptops', 'Monitors', 'Network Infrastructure', 'Tablets', 'Smartphones', 'Docking Stations'],
                weights=[20, 35, 15, 5, 10, 15],
                k=1
            )[0]
            generator.create_asset(categories[cat_choice])
            progress_bar(i + 1, remaining, prefix="      Stocking Progress  ")
        
        print(f"\n{Colors.GREEN}      ✔ Warehouse Stocked.{Colors.ENDC}")
    
    final_count = Asset.objects.count()
    print(f"\n{Colors.HEADER}{'='*70}")
    print(f"   OPERATION COMPLETE")
    print(f"   Total Assets: {Colors.BOLD}{final_count}{Colors.ENDC}")
    print(f"{'='*70}{Colors.ENDC}")

if __name__ == '__main__':
    run_seed()