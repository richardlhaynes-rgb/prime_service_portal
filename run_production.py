import os
import sys
import socket
import django
from waitress import serve
from config.wsgi import application

# Initialize Django to access version info
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def start_server():
    # ANSI Color Codes for that "Professional Terminal" look
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    # Dynamically pull Hostname and IP Address
    hostname = socket.gethostname()
    try:
        # Gets the primary IP address (works best on local networks)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
    except Exception:
        ip_address = "127.0.0.1"

    print("==========================================================")
    print(f"{GREEN}  PRIME Service Portal - PRODUCTION ENGINE{ENDC}")
    print("==========================================================")
    print(f"\n[INFO] Environment: {BOLD}Production (Waitress){ENDC}")
    print(f"[INFO] Django Version: {django.get_version()}")
    print(f"[INFO] Database: PostgreSQL 18.1")
    print(f"[INFO] Threads: 32 (Enterprise Scale)")
    
    print(f"\n{CYAN}--- NETWORK ACCESS ---{ENDC}")
    print(f"Local Access:   http://localhost:8000")
    print(f"Hostname:       http://{hostname}:8000")
    print(f"Network IP:     http://{ip_address}:8000")
    
    print(f"\n{CYAN}--- DOCUMENTATION ---{ENDC}")
    print(f"System Manual:  {os.path.join(os.getcwd(), 'SYSTEM_MANUAL.md')}")
    print(f"Purpose:        Business Continuity & Disaster Recovery")

    print(f"\n{BLUE}To stop the server, press CTRL+C or close this window.{ENDC}")
    print("\n" + "-"*58 + "\n")

    # Start Waitress on 0.0.0.0 to listen to the whole network
    serve(application, host='0.0.0.0', port=8000, threads=32, channel_timeout=60)

if __name__ == "__main__":
    start_server()