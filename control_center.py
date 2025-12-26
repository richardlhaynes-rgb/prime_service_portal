import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import shutil
from datetime import datetime

def run_command(command, title):
    try:
        subprocess.Popen(['cmd.exe', '/c', 'start', f'"{title}"', 'cmd.exe', '/k', command])
    except Exception as e:
        messagebox.showerror("Error", f"Could not start {title}: {str(e)}")

def smart_backup():
    try:
        source_dir = r'C:\Projects\prime_service_portal'
        base_backup_dir = r'G:\My Drive\development\portal_backups'
        
        now = datetime.now()
        date_str = now.strftime("%m_%d_%Y_%H%M")
        root_backup_path = os.path.join(base_backup_dir, date_str)
        
        db_folder = os.path.join(root_backup_path, "PostgreSQL")
        project_folder = os.path.join(root_backup_path, "prime_service_portal")

        os.makedirs(db_folder, exist_ok=True)
        
        # Database Backup
        backup_file = os.path.join(db_folder, "portal_db_backup.sql")
        db_cmd = f"pg_dump -U postgres prime_service_portal > \"{backup_file}\""
        
        db_result = subprocess.run(db_cmd, shell=True, capture_output=True, text=True)
        if db_result.returncode != 0:
            raise Exception(f"Database backup failed: {db_result.stderr}")

        # Full Project Copy (inc venv)
        shutil.copytree(source_dir, project_folder)

        messagebox.showinfo("Success", f"Full System Snapshot Completed!\nLocation: Google Drive")
        
    except Exception as e:
        messagebox.showerror("Backup Error", f"Snapshot aborted: {str(e)}")

# --- UI Dashboard Setup ---
root = tk.Tk()
root.title("PRIME Portal: Command & Control")
root.geometry("520x720") # Adjusted width for better text fit
root.configure(bg="#0f172a")

# Header
tk.Label(root, text="PRIME SERVICE PORTAL", fg="#38bdf8", bg="#0f172a", font=("Arial", 18, "bold")).pack(pady=(30, 0))
tk.Label(root, text="Mission Critical Control Center", fg="#94a3b8", bg="#0f172a", font=("Arial", 11)).pack(pady=(0, 30))

def create_button_group(btn_text, btn_color, desc_text, cmd_func):
    frame = tk.Frame(root, bg="#0f172a")
    frame.pack(pady=12, fill='x', padx=50)
    
    btn = tk.Button(frame, text=btn_text, bg=btn_color, fg="white", 
                    font=("Arial", 12, "bold"), height=2, bd=0, 
                    cursor="hand2", command=cmd_func)
    btn.pack(fill='x')
    
    # Description shortened to fit on one line
    desc = tk.Label(frame, text=desc_text, fg="#64748b", bg="#0f172a", 
                    font=("Arial", 9), justify="center")
    desc.pack(pady=4)

# --- Button Definitions ---
create_button_group("🚀 START PRODUCTION SITE", "#10b981", 
                    "Launch the Waitress engine for network-wide access.", 
                    lambda: run_command("Start_Portal.bat", "PRODUCTION"))

create_button_group("🔄 REFRESH SYSTEM ASSETS", "#3b82f6", 
                    "Sync logos and CSS to the production static server.", 
                    lambda: run_command("python manage.py collectstatic --noinput", "STATIC SYNC"))

create_button_group("📥 REFRESH TICKETS", "#6366f1", 
                    "Run background task to sync latest ticket data.", 
                    lambda: run_command("refresh_tickets.bat", "TICKET SYNC"))

create_button_group("☁️ FULL CLOUD SNAPSHOT", "#f59e0b", 
                    "Backup Database and entire Project folder to Google Drive.", 
                    smart_backup)

create_button_group("🛠️ START DEV SERVER", "#475569", 
                    "Launch internal local test mode for code changes.", 
                    lambda: run_command("python manage.py runserver", "DEV MODE"))

# Status Bar
footer = tk.Label(root, text="PostgreSQL 18.1 | Waitress | Django 5.2.8", 
                  fg="#334155", bg="#0f172a", font=("Arial", 8))
footer.pack(side="bottom", pady=15)

root.mainloop()