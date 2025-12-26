import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
from PIL import Image, ImageTk
import subprocess, os, threading, ctypes
from datetime import datetime

# --- 1. SYSTEM INITIALIZATION ---
CREATE_NO_WINDOW = 0x08000000
script_dir = r"C:\Projects\prime_service_portal"
os.chdir(script_dir)

try:
    my_app_id = 'PRIME_AE.Portal.Cockpit.v2.4.2'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
except: pass

# --- 2. THEME DEFINITION ---
CLR_BG, CLR_SIDEBAR, CLR_ACCENT = "#0f172a", "#1e293b", "#38bdf8"
CLR_WHITE, CLR_OFFWHITE = "#ffffff", "#94a3b8"
BTN_PROD, BTN_DEV, BTN_BLUE = "#065f46", "#334155", "#1e40af"
BTN_PURPLE, BTN_GIT, BTN_DANGER = "#5b21b6", "#c2410c", "#991b1b"
CLR_BORDER = "#334155"

running_pids = {"PROD": None, "DEV": None}

def log_message(msg, is_raw=False, is_status=False):
    try:
        log_box.config(state='normal')
        if is_raw:
            log_box.insert(tk.END, msg, 'white')
        else:
            now = datetime.now().strftime("%H:%M:%S")
            log_box.insert(tk.END, f"[{now}] ", 'ts')
            color = 'success' if is_status else 'white'
            log_box.insert(tk.END, f"{msg}\n", color)
        log_box.see(tk.END)
        log_box.config(state='disabled')
    except: pass

# --- 3. SAFETY & PORT-KILL LOGIC ---
def stop_server(key):
    pid = running_pids.get(key)
    if pid:
        log_message(f"⚪ Terminating {key} instance...")
        subprocess.run(f"taskkill /F /T /PID {pid}", shell=True, creationflags=CREATE_NO_WINDOW)
        running_pids[key] = None
        log_message(f"{key} has been safely offlined.", is_status=True)

def safe_exit():
    """Surgically kills anything on Port 8000 and standard Python engines."""
    subprocess.run("taskkill /F /IM pythonw.exe /T", shell=True, creationflags=CREATE_NO_WINDOW)
    subprocess.run("taskkill /F /IM python.exe /T", shell=True, creationflags=CREATE_NO_WINDOW)
    try:
        port_cmd = 'netstat -ano | findstr :8000'
        result = subprocess.check_output(port_cmd, shell=True, text=True, creationflags=CREATE_NO_WINDOW)
        for line in result.strip().split('\n'):
            parts = line.split()
            if len(parts) > 4:
                pid = parts[-1]
                subprocess.run(f"taskkill /F /T /PID {pid}", shell=True, creationflags=CREATE_NO_WINDOW)
    except: pass

    active_servers = [k for k, v in running_pids.items() if v is not None]
    if active_servers:
        if messagebox.askokcancel("Active Processes", "Shut down servers and exit Cockpit?"):
            for server in active_servers: stop_server(server)
            root.destroy()
    else: root.destroy()

def run_git_push(btn):
    summary = simpledialog.askstring("Git Commit", "Enter summary:", parent=root)
    if not summary: return
    def task():
        btn.config(state='disabled', bg=CLR_BORDER)
        log_message(f"--- STARTING GIT DEPLOY: {summary} ---")
        for cmd in ['git add .', f'git commit -m "{summary}"', 'git push']:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True, creationflags=CREATE_NO_WINDOW)
            for line in iter(p.stdout.readline, ''): log_message(line, is_raw=True)
            p.wait()
        btn.config(state='normal', bg=btn.orig)
        log_message("--- GIT DEPLOY COMPLETED ---")
    threading.Thread(target=task, daemon=True).start()

def run_server(cmd, key, b_start, b_stop):
    def task():
        try:
            log_message(f"🚀 Initializing {key} Service...")
            b_start.config(state='disabled', bg=CLR_BORDER)
            b_stop.config(state='normal', bg=BTN_DANGER)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True, bufsize=1, universal_newlines=True, creationflags=CREATE_NO_WINDOW)
            running_pids[key] = p.pid
            log_message(f"System status: ONLINE (ID: {p.pid})", is_status=True)
            for line in iter(p.stdout.readline, ''): log_message(line, is_raw=True)
            p.wait()
        except Exception as e: log_message(f"ERROR: {e}")
        finally: 
            running_pids[key] = None
            b_start.config(state='normal', bg=b_start.orig)
            b_stop.config(state='disabled', bg="#450a0a")
    threading.Thread(target=task, daemon=True).start()

# --- 4. UI CONSTRUCTION ---
root = tk.Tk()
root.title("PRIME Portal | Cockpit")
W_WIDTH, W_HEIGHT = 1200, 850 
sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry(f'{W_WIDTH}x{W_HEIGHT}+{int((sw/2)-(W_WIDTH/2))}+{int((sh/2)-(W_HEIGHT/2))}')
root.resizable(False, False)
root.configure(bg=CLR_BG)
root.protocol("WM_DELETE_WINDOW", safe_exit)

if os.path.exists('control_icon.ico'): root.iconbitmap('control_icon.ico')

side = tk.Frame(root, bg=CLR_SIDEBAR, width=380)
side.pack(side="left", fill="y")
side.pack_propagate(False)

# Logo
logo_path = os.path.join(script_dir, "static", "images", "logo_white.png")
try:
    img = Image.open(logo_path)
    img = img.resize((240, 110), Image.Resampling.LANCZOS)
    prime_logo = ImageTk.PhotoImage(img)
    tk.Label(side, image=prime_logo, bg=CLR_SIDEBAR).pack(pady=(35, 10))
except:
    tk.Label(side, text="PRIME AE", font=("Arial", 24, "bold"), bg=CLR_SIDEBAR, fg="white").pack(pady=(40, 10))

tk.Label(side, text="PRIME PORTAL", fg=CLR_ACCENT, bg=CLR_SIDEBAR, font=("Arial", 16, "bold")).pack()
tk.Label(side, text="ADMIN CONSOLE V2.4.2", fg=CLR_OFFWHITE, bg=CLR_SIDEBAR, font=("Arial", 8, "bold")).pack(pady=(0, 20))

def nav_card(label, desc, cmd, clr, is_srv=False, is_git=False, key=None):
    container = tk.Frame(side, bg=CLR_SIDEBAR)
    container.pack(pady=6, fill='x', padx=30)
    tk.Label(container, text=desc, fg=CLR_WHITE, bg=CLR_SIDEBAR, font=("Arial", 9, "bold"), justify="left", wraplength=320).pack(anchor="w", pady=(0, 2))
    
    if is_srv:
        b_frame = tk.Frame(container, bg=CLR_SIDEBAR)
        b_frame.pack(fill='x')
        b1 = tk.Button(b_frame, text=f"START {label}", bg=clr, fg="white", font=("Arial", 9, "bold"), height=2, bd=0, cursor="hand2")
        b1.orig = clr
        b1.pack(side="left", expand=True, fill='x', padx=(0, 2))
        b2 = tk.Button(b_frame, text="STOP", bg="#450a0a", fg="white", font=("Arial", 9, "bold"), height=2, width=6, bd=0, state='disabled')
        b2.pack(side="right")
        b1.config(command=lambda: run_server(cmd, key, b1, b2))
        b2.config(command=lambda: stop_server(key))
    else:
        b = tk.Button(container, text=label, bg=clr, fg="white", font=("Arial", 9, "bold"), height=2, bd=0, cursor="hand2")
        b.orig = clr
        if is_git: b.config(command=lambda: run_git_push(b))
        else: b.config(command=lambda: threading.Thread(target=lambda: subprocess.run(cmd, shell=True, creationflags=CREATE_NO_WINDOW), daemon=True).start())
        b.pack(fill='x')

nav_card("PRODUCTION", "Launch network-ready Waitress engine.", "python run_production.py", BTN_PROD, is_srv=True, key="PROD")
nav_card("DEV SERVER", "Internal test mode for local code changes.", "python manage.py runserver", BTN_DEV, is_srv=True, key="DEV")
tk.Frame(side, bg=CLR_BORDER, height=1).pack(fill="x", padx=45, pady=10)
nav_card("REFRESH ASSETS", "Synchronize static files and media.", "python manage.py collectstatic --noinput", BTN_BLUE)
nav_card("RUN MIGRATIONS", "Update database schemas and tables.", "python manage.py makemigrations && python manage.py migrate", BTN_PURPLE)
tk.Frame(side, bg=CLR_BORDER, height=1).pack(fill="x", padx=45, pady=10)
nav_card("COMMIT & DEPLOY", "Commit all changes and push to Git repo.", "", BTN_GIT, is_git=True)

# HIGH-VISIBILITY FOOTER
footer_txt = "PRIME AE Group, Inc.\nPostgreSQL 18.1 | Django 5.2.8"
footer = tk.Label(side, text=footer_txt, fg=CLR_WHITE, bg=CLR_SIDEBAR, 
                  font=("Arial", 9, "bold"), justify="center")
footer.pack(side="bottom", pady=25)

main = tk.Frame(root, bg=CLR_BG)
main.pack(side="right", fill="both", expand=True, padx=35, pady=35)
tk.Label(main, text="SYSTEM ACTIVITY LOG", fg=CLR_WHITE, bg=CLR_BG, font=("Arial", 9, "bold")).pack(anchor="w")
log_box = scrolledtext.ScrolledText(main, bg="#020617", fg="#10b981", font=("Consolas", 10), bd=0, padx=15, pady=15, highlightthickness=1, highlightbackground=CLR_BORDER)
log_box.pack(fill="both", expand=True, pady=(10, 0))
log_box.tag_configure('ts', foreground=CLR_ACCENT)
log_box.tag_configure('white', foreground=CLR_WHITE)
log_box.tag_configure('success', foreground="#10b981")

log_message("v2.4.2 Ready.")
root.mainloop()