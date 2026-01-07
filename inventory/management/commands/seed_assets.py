import time
import random
import datetime
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.contrib.auth import get_user_model
from inventory.models import HardwareAsset, AssetCategory 

User = get_user_model()

# --- CONFIGURATION ---
TARGET_TOTAL = 325 
START_DATE_RANGE = datetime.date(2022, 1, 1)

# --- DATASETS ---
MODELS_DB = {
    'Laptops': [
        ('Dell', 'Precision 5680 Mobile Workstation', 2400, 3200),
        ('Dell', 'Latitude 7440 Ultralight', 1600, 2100),
        ('Dell', 'XPS 15 9530', 1800, 2500),
        ('HP', 'ZBook Firefly 16 G10', 1900, 2600),
        ('Lenovo', 'ThinkPad X1 Carbon Gen 11', 1700, 2300),
        ('Microsoft', 'Surface Laptop Studio 2', 2200, 2900)
    ],
    'Desktops': [
        ('Dell', 'OptiPlex 7010 Micro', 800, 1200),
        ('Dell', 'Precision 3660 Tower', 1500, 2200),
        ('HP', 'Elite Mini 800 G9', 900, 1300),
        ('Lenovo', 'ThinkCentre M70q Gen 4', 750, 1100),
        ('Apple', 'Mac mini (M2 Pro)', 1299, 1699),
        ('Apple', 'Mac Studio (M2 Max)', 1999, 2599)
    ],
    'Servers': [
        ('Dell', 'PowerEdge R760 Rack Server', 5000, 12000),
        ('Dell', 'PowerEdge R450', 3500, 6000),
        ('HPE', 'ProLiant DL380 Gen11', 6000, 14000),
        ('HPE', 'ProLiant MicroServer Gen10 Plus', 800, 1500)
    ],
    'Smartphones': [
        ('Apple', 'iPhone 15 Pro Max', 1199, 1599),
        ('Apple', 'iPhone 15 Pro', 999, 1299),
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
        ('Netgear', 'Nighthawk M6 Pro', 450, 500)
    ],
    'Monitors': [
        ('Dell', 'UltraSharp U2724D', 350, 450),
        ('Dell', 'P2422H', 180, 220),
        ('HP', 'E27 G5 FHD', 250, 300),
        ('LG', '27UK850-W 4K', 400, 500),
        ('Samsung', 'Odyssey G9 OLED', 1200, 1500)
    ],
    'Docking Stations': [
        ('Dell', 'WD19S 180W', 220, 280),
        ('Dell', 'WD22TB4 Thunderbolt 4', 320, 380),
        ('HP', 'Thunderbolt Dock G4', 280, 340),
        ('Kensington', 'SD5700T Thunderbolt 4', 250, 300)
    ],
    'Network Infrastructure': [
        ('Cisco', 'Catalyst 9200L 48-Port', 3500, 4500),
        ('Cisco', 'Meraki MX68 Firewall', 900, 1400),
        ('Ubiquiti', 'Dream Machine Pro SE', 499, 499),
        ('Ubiquiti', 'Switch Pro 48 PoE', 1099, 1099),
        ('Palo Alto', 'PA-440 Firewall', 1200, 1800)
    ],
    'Printers & Plotters': [
        ('HP', 'DesignJet T650 Large Format Plotter', 1500, 2500),
        ('HP', 'Color LaserJet Pro MFP M479fdw', 500, 700),
        ('Canon', 'imageRUNNER ADVANCE DX', 3000, 5000),
        ('Brother', 'HL-L6200DW Business Laser', 200, 300)
    ],
    'AV & VR Equipment': [
        ('Meta', 'Quest 3 512GB', 649, 649),
        ('HTC', 'Vive Pro 2 Full Kit', 1399, 1399),
        ('Logitech', 'Rally Bar Video Bar', 3500, 4000),
        ('Epson', 'PowerLite L730U Laser Projector', 2200, 2800),
        ('Poly', 'Studio X50 Video Bar', 2500, 3000)
    ],
    'Peripherals': [
        ('Logitech', 'MX Master 3S Mouse', 99, 99),
        ('Logitech', 'MX Keys S Keyboard', 109, 109),
        ('Jabra', 'Evolve2 65 Headset', 180, 220),
        ('Poly', 'Voyager Focus 2 UC', 200, 250),
        ('APC', 'Smart-UPS 1500VA', 500, 700)
    ]
}

# --- SYSTEM SPECS POOLS ---
CPU_POOLS = ['Intel Core i7-1365U', 'Intel Core i9-13900H', 'AMD Ryzen 7 PRO', 'Apple M2 Pro', 'Apple M3 Max']
SERVER_CPU_POOLS = ['Intel Xeon Gold 6430', 'AMD EPYC 9354', 'Intel Xeon Silver 4410']
GPU_POOLS = ['NVIDIA RTX 2000 Ada', 'NVIDIA RTX 4050', 'Intel Iris Xe', 'Integrated Graphics']
RAM_POOLS = ['16 GB', '32 GB', '64 GB', '128 GB']
SERVER_RAM_POOLS = ['64 GB', '128 GB', '256 GB', '512 GB']
RAM_TYPE_POOLS = ['DDR5', 'DDR4', 'LPDDR5', 'Unified Memory']

# Storage split logic
STORAGE_PRI_POOLS = ['256 GB SSD', '512 GB SSD', '1 TB SSD', '2 TB SSD']
STORAGE_SEC_POOLS = ['None', 'None', 'None', 'None', 'None', 'None', 'None', '1 TB HDD', '2 TB HDD', '4 TB HDD']
SERVER_STORAGE_POOLS = ['2x 480GB SSD (RAID 1)', '4x 1.92TB SSD (RAID 5)', '8x 2.4TB SAS HDD (RAID 6)']

OS_POOLS = {
    'Laptop': ['Windows 11 Pro', 'Windows 10 Enterprise', 'macOS Sonoma'],
    'Server': ['Windows Server 2022 Standard', 'Windows Server 2019', 'Ubuntu Server 22.04 LTS', 'Red Hat Enterprise Linux 9'],
    'Phone': ['iOS 17.2', 'Android 14'],
    'Tablet': ['iPadOS 17.1', 'Android 13']
}

# --- MONITOR SPECS POOLS ---
MONITOR_SPECS = {
    'sizes': ['24-inch', '27-inch', '32-inch', '34-inch Ultrawide', '38-inch Ultrawide', '49-inch Super Ultrawide'],
    'resolutions': ['1920 x 1080 (FHD)', '2560 x 1440 (QHD)', '3440 x 1440 (UWQHD)', '3840 x 2160 (4K UHD)', '5120 x 1440 (DQHD)'],
    'panels': ['IPS', 'VA', 'TN', 'OLED'],
    'refresh': ['60 Hz', '75 Hz', '120 Hz', '144 Hz', '165 Hz +'],
    'colors': ['Black', 'Silver', 'White', 'Space Gray'],
}

MAC_OUI = {'Dell': '00:14:22', 'HP': 'FC:15:B4', 'Apple': '00:1C:B3', 'Cisco': '00:00:0C', 'HPE': 'D8:D3:85', 'Ubiquiti': 'F4:92:BF'}
CARRIERS = ['Verizon Wireless', 'AT&T Business', 'T-Mobile Enterprise']

class Command(BaseCommand):
    help = 'Wipes the Asset table and seeds 325 realistic items. Use --clear to wipe only.'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Skip safety checks')
        parser.add_argument('--clear', action='store_true', help='Wipe data only, do not seed.')

    def handle(self, *args, **options):
        # 1. VISUALS
        self.stdout.write(self.style.SUCCESS("\n=========================================="))
        self.stdout.write(self.style.SUCCESS("   PRIME ASSET ORCHESTRATOR (SYSTEM COMMAND)"))
        self.stdout.write(self.style.SUCCESS("==========================================\n"))

        # 2. SAFETY CHECK
        if not options['force']:
            self.stdout.write(self.style.WARNING("!!! WARNING: MANUAL MODE DETECTED !!!"))
            self.stdout.write("This will DELETE ALL ASSETS. Use --force to skip this prompt.")
            confirm = input("Type 'DESTROY' to continue: ")
            if confirm != 'DESTROY':
                self.stdout.write(self.style.ERROR("Aborted."))
                return

        # 3. PURGE
        self.stdout.write(self.style.MIGRATE_HEADING("[1/4] Wiping Database..."))
        with connection.cursor() as cursor:
            cursor.execute(f"TRUNCATE TABLE {HardwareAsset._meta.db_table} RESTART IDENTITY CASCADE;")
        self.stdout.write(self.style.SUCCESS("      Database Cleaned."))

        # 3a. EXIT IF CLEAR ONLY
        if options['clear']:
            self.stdout.write(self.style.SUCCESS("      Data wipe complete. No assets generated."))
            return

        # 4. CATEGORIES
        self.stdout.write(self.style.MIGRATE_HEADING("[2/4] Building Taxonomy..."))
        required_cats = [
            'Laptops', 'Desktops', 'Servers',
            'Smartphones', 'Tablets', 'Mobile Hotspots', 
            'Monitors', 'Docking Stations', 
            'Network Infrastructure', 'Printers & Plotters',
            'AV & VR Equipment', 'Peripherals'
        ]
        categories = {}
        for name in required_cats:
            cat, _ = AssetCategory.objects.get_or_create(name=name)
            categories[name] = cat
        self.stdout.write(self.style.SUCCESS(f"      {len(categories)} Categories Active."))

        # 5. GENERATION HELPERS
        self.tag_counters = {
            'LT': 1000, 'DT': 1000, 'SRV': 1000,
            'PH': 2000, 'TB': 3000, 'HS': 4000, 
            'MN': 5000, 'DK': 6000, 'NET': 8000, 
            'PRN': 7000, 'AV': 5500, 'PER': 9000, 
            'GEN': 9900
        }

        def get_next_tag(category_name):
            prefix_map = {
                'Laptops': 'LT', 'Desktops': 'DT', 'Servers': 'SRV',
                'Smartphones': 'PH', 'Tablets': 'TB', 'Mobile Hotspots': 'HS', 
                'Monitors': 'MN', 'Docking Stations': 'DK', 'Network Infrastructure': 'NET',
                'Printers & Plotters': 'PRN', 'AV & VR Equipment': 'AV', 'Peripherals': 'PER'
            }
            prefix = prefix_map.get(category_name, 'GEN')
            self.tag_counters[prefix] += random.randint(1, 3)
            return f"PRIME-{prefix}-{self.tag_counters[prefix]}"

        def create_single_asset(cat, user=None):
            model_data = MODELS_DB.get(cat.name, MODELS_DB['Laptops'])
            manuf, model, c_min, c_max = random.choice(model_data)
            
            # Status Logic
            if cat.name == 'Peripherals':
                status = 'Deployed' if user else random.choices(['In Stock', 'Maintenance', 'Retired'], weights=[90, 5, 5], k=1)[0]
            elif cat.name == 'Servers':
                status = 'Deployed' 
            else:
                status = 'Deployed' if user else random.choices(['In Stock', 'Maintenance', 'Retired'], weights=[85, 10, 5], k=1)[0]
            
            # --- SPECS GENERATION LOGIC ---
            specs = {}
            
            # A. CLIENT COMPUTING
            if cat.name in ['Laptops', 'Desktops']:
                specs['hostname'] = f"CORP-{manuf[:3].upper()}-{random.randint(100,999)}"
                specs['cpu'] = random.choice(CPU_POOLS)
                specs['ram'] = random.choice(RAM_POOLS)
                
                if manuf == 'Apple':
                    specs['ram_type'] = 'Unified Memory'
                    specs['gpu'] = 'Integrated Apple GPU'
                    specs['os'] = 'macOS Sonoma'
                else:
                    specs['ram_type'] = random.choice(RAM_TYPE_POOLS)
                    specs['gpu'] = random.choice(GPU_POOLS)
                    specs['os'] = random.choice(OS_POOLS['Laptop'])

                specs['storage_pri'] = random.choice(STORAGE_PRI_POOLS)
                specs['storage_sec'] = random.choice(STORAGE_SEC_POOLS)
                
                if specs['storage_sec'] != 'None':
                    specs['storage'] = f"{specs['storage_pri']} + {specs['storage_sec']}"
                else:
                    specs['storage'] = specs['storage_pri']

                specs['net_mac'] = f"{MAC_OUI.get(manuf, '00:00:00')}:{random.randint(10,99)}:{random.randint(10,99)}:{random.randint(10,99)}"
                specs['net_assignment'] = 'DHCP'

            # B. SERVERS
            elif cat.name == 'Servers':
                specs['hostname'] = f"SVR-{random.choice(['DC', 'FILE', 'APP', 'SQL'])}-{random.randint(0,9)}"
                specs['os'] = random.choice(OS_POOLS['Server'])
                specs['cpu'] = random.choice(SERVER_CPU_POOLS)
                specs['ram'] = random.choice(SERVER_RAM_POOLS)
                specs['ram_type'] = 'ECC DDR5'
                specs['storage_pri'] = random.choice(SERVER_STORAGE_POOLS)
                specs['storage'] = specs['storage_pri']
                
                specs['net_assignment'] = 'Manual'
                specs['net_ipv4'] = f"10.50.10.{random.randint(10, 50)}"
                specs['net_mac'] = f"{MAC_OUI.get(manuf, '00:00:00')}:{random.randint(10,99)}:{random.randint(10,99)}:{random.randint(10,99)}"
                specs['net_desc'] = "Primary NIC (10GbE)"

            # C. MONITORS
            elif cat.name == 'Monitors':
                if 'OLED' in model:
                    specs['disp_size'] = '49-inch Super Ultrawide'
                    specs['disp_res'] = '5120 x 1440 (DQHD)'
                    specs['disp_panel'] = 'OLED'
                    specs['disp_refresh'] = '144 Hz'
                    specs['disp_curved'] = True
                else:
                    specs['disp_size'] = random.choice(MONITOR_SPECS['sizes'])
                    if 'Ultrawide' in specs['disp_size']:
                        specs['disp_res'] = '3440 x 1440 (UWQHD)'
                        specs['disp_curved'] = True
                    elif '32-inch' in specs['disp_size']:
                        specs['disp_res'] = '3840 x 2160 (4K UHD)'
                        specs['disp_curved'] = False
                    else:
                        specs['disp_res'] = random.choice(['1920 x 1080 (FHD)', '2560 x 1440 (QHD)'])
                        specs['disp_curved'] = False

                    specs['disp_panel'] = random.choice(MONITOR_SPECS['panels'])
                    specs['disp_refresh'] = random.choice(MONITOR_SPECS['refresh'])

                specs['disp_color'] = random.choice(MONITOR_SPECS['colors'])
                base_ports = ['HDMI', 'DisplayPort']
                if random.random() > 0.5: base_ports.append('USB-C / Thunderbolt')
                if random.random() > 0.7: base_ports.append('USB Hub')
                specs['disp_ports'] = base_ports

            # D. MOBILE
            elif cat.name in ['Smartphones', 'Tablets']:
                specs['os'] = random.choice(OS_POOLS.get('Phone' if cat.name == 'Smartphones' else 'Tablet'))
                specs['storage'] = random.choice(['128 GB', '256 GB'])
                specs['mob_enabled'] = True
                specs['mob_carrier'] = random.choice(CARRIERS)
                specs['mob_phone'] = f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}"
                specs['mob_imei'] = str(random.randint(100000000000000, 999999999999999))
                specs['mob_status'] = 'Active'

            # E. INFRASTRUCTURE & PRINTERS
            elif cat.name in ['Network Infrastructure', 'Printers & Plotters']:
                specs['net_mac'] = f"{MAC_OUI.get(manuf, '00:00:00')}:{random.randint(10,99)}:{random.randint(10,99)}:{random.randint(10,99)}"
                specs['net_assignment'] = 'Manual'
                ip_subnet = 1 if cat.name == 'Network Infrastructure' else 50
                specs['net_ipv4'] = f"10.50.{ip_subnet}.{random.randint(2,250)}"
                if cat.name == 'Network Infrastructure':
                    specs['net_vlan'] = "1 (Mgmt)"
                else:
                    specs['net_vlan'] = "30 (Printers)"

            # F. AV & VR
            elif cat.name == 'AV & VR Equipment':
                specs['notes'] = "Assigned to Conference Room or VR Lab."

            # CREATE RECORD
            HardwareAsset.objects.create(
                asset_tag=get_next_tag(cat.name),
                serial_number="".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8)),
                manufacturer=manuf,
                model_number=model,
                category=cat,
                status=status,
                assigned_to=user,
                vendor="CDW-G",
                purchase_date=START_DATE_RANGE,
                warranty_expiration=datetime.date.today() + datetime.timedelta(days=730),
                cost=random.randint(c_min, c_max),
                specs=specs,
                notes="Generated via Command."
            )

        # 6. ASSIGNMENT LOOP
        users = list(User.objects.all())
        self.stdout.write(self.style.MIGRATE_HEADING(f"[3/4] Provisioning Kits for {len(users)} Users..."))
        
        count = 0
        for user in users:
            # Everyone gets a standard kit
            create_single_asset(categories['Smartphones'], user)
            create_single_asset(categories['Laptops'], user)
            create_single_asset(categories['Docking Stations'], user)
            create_single_asset(categories['Monitors'], user)
            create_single_asset(categories['Peripherals'], user) 
            
            # VIPs get extra stuff
            if random.random() > 0.8:
                create_single_asset(categories['Tablets'], user)
            if random.random() > 0.9:
                create_single_asset(categories['Mobile Hotspots'], user)
            
            count += 5
            self.stdout.write(".", ending="")
            self.stdout.flush()
        
        self.stdout.write(self.style.SUCCESS(f"\n      {count} Assets Deployed."))

        # 7. FILLER
        remaining = TARGET_TOTAL - count
        if remaining > 0:
            self.stdout.write(self.style.MIGRATE_HEADING(f"[4/4] Stocking {remaining} Spare Items..."))
            for _ in range(remaining):
                cat = random.choices(
                    list(categories.values()), 
                    weights=[15, 5, 2, 5, 5, 2, 20, 10, 3, 3, 5, 25], 
                    k=1
                )[0]
                create_single_asset(cat)
                self.stdout.write(".", ending="")
                self.stdout.flush()

        self.stdout.write(self.style.SUCCESS("\n\nMISSION COMPLETE."))