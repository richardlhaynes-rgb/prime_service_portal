"""
PRIME Service Portal - Developer Toolkit v6.30
--------------------------------------------------------------------------------
App Major Features:
1. Smart Backup Engine:
   - Auto-generates requirements.txt & captures pgpass.conf.

2. Recovery Dashboard:
   - List, Restore Guide, and File Browser views.

3. Database Ops Dashboard (STABLE):
   - Fixed Tuple Unpacking Crash (now correctly passes 8 values).
   - Removed obsolete init functions that caused startup errors.
   - "Total Commits" formatted with commas for readability.
   - "Visual Decay" graph logic preserved for smooth activity waves.

4. Dev Tools Cockpit:
   - Git Status, Environment Info, Quick File Access.
   - SMART COMMIT & PUSH: Uses venv activation to ensure credential inheritance.
   - DJANGO SHELL: One-click venv + manage.py shell access.

5. Server Control:
   - Graphs use "Fixed Height" mode (150px).

6. Architecture:
   - STRICT "Long-Hand" coding style (One command per line).
   - Detailed comments for every section.
--------------------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import scrolledtext
from tkinter import ttk
import subprocess
import os
import threading
import ctypes
import shutil
import time
import random 
from datetime import datetime
from datetime import timedelta
import webbrowser
import socket
import getpass
import re
import sys

# -----------------------------------------------------------------------------
# DEPENDENCY CHECKS (CRASH PREVENTION)
# -----------------------------------------------------------------------------

# Check for Pillow (Image Processing)
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Check for tkcalendar (Date Picker)
try:
    from tkcalendar import Calendar
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False

# Check for psutil (System Telemetry)
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Check for psycopg2 (PostgreSQL Driver)
try:
    import psycopg2
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

# =============================================================================
# 1. SYSTEM INITIALIZATION & WORK AREA LOGIC
# =============================================================================

# Flag to prevent subprocesses from opening black command windows
CREATE_NO_WINDOW = 0x08000000

# Base Paths (Adjust as needed)
SCRIPT_DIR = r"C:\Projects\prime_service_portal"
BACKUP_ROOT = r"G:\My Drive\development\portal_backups"

# Ensure we are working in the correct directory
os.chdir(SCRIPT_DIR)

# Set AppID so Windows Taskbar shows the correct icon
try:
    my_app_id = 'PRIME.ServicePortal.Toolkit.v6.30'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
except:
    pass

def get_work_area():
    """
    Gets the usable screen rectangle (excluding the Windows Taskbar).
    Used to center the window perfectly in the visual workspace.
    """
    try:
        class RECT(ctypes.Structure):
            _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long),
                        ('right', ctypes.c_long), ('bottom', ctypes.c_long)]
        rect = RECT()
        ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(rect), 0)
        return rect.left, rect.top, rect.right, rect.bottom
    except:
        return 0, 0, 1920, 1080 

# =============================================================================
# 2. THEME DEFINITION
# =============================================================================
THEME = {
    'status_idle': '#64748b',     
    'status_active': '#10b981',   
    'status_error': '#ef4444',    
    'status_warning': '#f59e0b',
    'bg_primary': '#0f172a',      
    'bg_card': '#1e293b',         
    'bg_console': '#020617',
    'text_primary': '#f8fafc',    
    'text_secondary': '#94a3b8',  
    'text_console': '#10b981',   
    'text_muted': '#64748b',
    'accent_blue': '#38bdf8',     
    'accent_orange': '#f15d2a',
    'accent_pink': '#f472b6',     
    'accent_purple': '#a78bfa',
    'accent_yellow': '#facc15',
    'border': '#334155',          
    'graph_line': '#38bdf8',
    'btn_success': '#059669',     
    'btn_danger': '#b91c1c',      
    'btn_info': '#3b82f6',        
    'btn_purple': '#7c3aed',
    'btn_secondary': '#475569',   
    'btn_backup': '#4338ca',      
    'btn_disabled': '#1e293b'
}

FONTS = {
    'header': ('Segoe UI', 18, 'bold'),
    'subheader': ('Segoe UI', 14, 'bold'),
    'title': ('Segoe UI', 12, 'bold'),
    'body_bold': ('Segoe UI', 10, 'bold'),
    'big_value': ('Segoe UI', 24, 'bold'), 
    'small': ('Segoe UI', 9),
    'console': ('Consolas', 10),
    'button': ('Segoe UI', 10, 'bold'),
}

ICONS = {
    'play': '▶', 'stop': '⏹', 'refresh': '⟳', 'lightning': '⚡',
    'shield': '🛡', 'database': '🗄', 'terminal': '>_', 'python': '>>>',
    'folder': '📁', 'file': '📄', 'git': '⎇', 'calendar': '📅', 'trash': '🗑',
    'seed': '🌱', 'rocket': '🚀', 'gear': '⚙', 'check': '✓',
    'cpu': '🖥', 'ram': '💾', 'globe': '🌐', 'link': '🔗',
    'expand': '▲', 'collapse': '▼', 'search': '🔍', 'back': '⬅',
    'code': '📝', 'branch': '🌱', 'django': 'DJ'
}

# =============================================================================
# 3. TELEMETRY ENGINE (PERSISTENT CONNECTION)
# =============================================================================
class DatabaseMonitor:
    """
    Manages a PERSISTENT connection to the database.
    Handles 'Visual Decay' logic to make graphs look alive.
    """
    def __init__(self):
        self.conn = None
        self.last_time = time.monotonic()
        
        # Absolute Counters (Raw from DB)
        self.last_xact = 0
        self.last_read = 0
        self.last_write = 0
        
        # Display Values (With Decay applied for smooth visuals)
        self.display_tps = 0.0
        self.display_reads = 0.0
        self.display_writes = 0.0
        
        self.initialized = False

    def connect(self):
        """Establishes a persistent connection."""
        if not HAS_PSYCOPG2:
            return False
        try:
            self.conn = psycopg2.connect(dbname="prime_service_portal", user="postgres", host="localhost", port="5432")
            self.conn.autocommit = True
            return True
        except:
            return False

    def poll(self):
        """
        Fetches stats and applies VISUAL DECAY.
        Returns: (Connections, TPS, Reads, Writes, SizeBytes, Cache%, Status, TotalCommits)
        """
        # Return default 8-tuple if driver missing
        if not HAS_PSYCOPG2:
            return 0, 0, 0, 0, 0, 0, "Driver Missing", 0

        # Reconnect if needed
        if self.conn is None or self.conn.closed:
            if not self.connect():
                return 0, 0, 0, 0, 0, 0, "No Connection", 0

        try:
            cur = self.conn.cursor()

            # Atomic Query: Fetch all counters in one go
            # Force float conversion to prevent decimal/float type mismatch
            query = """
                SELECT 
                    (SELECT count(*) FROM pg_stat_activity WHERE datname = 'prime_service_portal'),
                    (SELECT pg_database_size('prime_service_portal')),
                    sum(xact_commit + xact_rollback),
                    sum(tup_fetched + tup_returned),
                    sum(tup_inserted + tup_updated + tup_deleted),
                    sum(blks_hit),
                    sum(blks_read)
                FROM pg_stat_database 
                WHERE datname = 'prime_service_portal';
            """
            cur.execute(query)
            row = cur.fetchone()
            
            if not row:
                return 0, 0, 0, 0, 0, 0, "No Data", 0

            # Unpack and Force Float for Calc
            curr_conns = row[0] or 0
            curr_size = row[1] or 0
            curr_xact = float(row[2] or 0)
            curr_read = float(row[3] or 0)
            curr_write = float(row[4] or 0)
            blks_hit = float(row[5] or 0)
            blks_read = float(row[6] or 0)

            # Cache Ratio
            total_blks = blks_hit + blks_read
            if total_blks > 0:
                cache_ratio = (blks_hit / total_blks) * 100
            else:
                cache_ratio = 0.0

            # Time Delta calculation
            current_time = time.monotonic()
            time_delta = current_time - self.last_time
            
            # Prevent Division by Zero
            if time_delta < 0.1: 
                time_delta = 0.1

            # First Run Initialization
            if not self.initialized:
                self.last_time = current_time
                self.last_xact = curr_xact
                self.last_read = curr_read
                self.last_write = curr_write
                self.initialized = True
                # Return 8 values to match unpack expectation
                return curr_conns, 0, 0, 0, curr_size, cache_ratio, "Connected", curr_xact

            # --- CALCULATE RAW DELTAS ---
            delta_xact = curr_xact - self.last_xact
            delta_read = curr_read - self.last_read
            delta_write = curr_write - self.last_write

            # Calculate Rate per Second
            raw_tps = delta_xact / time_delta
            raw_reads = delta_read / time_delta
            raw_writes = delta_write / time_delta

            # Filter Startup/Reset Spikes
            if raw_tps < 0: raw_tps = 0
            if raw_reads < 0: raw_reads = 0
            if raw_writes < 0: raw_writes = 0
            
            # --- APPLY VISUAL DECAY ---
            # TPS Decay
            if raw_tps > self.display_tps:
                self.display_tps = raw_tps 
            else:
                self.display_tps = self.display_tps * 0.90 
                if self.display_tps < 0.1: 
                    self.display_tps = 0

            # Read Decay
            if raw_reads > self.display_reads:
                self.display_reads = raw_reads
            else:
                self.display_reads = self.display_reads * 0.90
                if self.display_reads < 0.1: 
                    self.display_reads = 0

            # Write Decay
            if raw_writes > self.display_writes:
                self.display_writes = raw_writes
            else:
                self.display_writes = self.display_writes * 0.90
                if self.display_writes < 0.1: 
                    self.display_writes = 0

            # Update State for next tick
            self.last_time = current_time
            self.last_xact = curr_xact
            self.last_read = curr_read
            self.last_write = curr_write

            # Return ALL 8 VALUES required by the main loop
            return curr_conns, self.display_tps, self.display_reads, self.display_writes, curr_size, cache_ratio, "Connected", curr_xact

        except Exception as e:
            # Return error tuple matching length
            return 0, 0, 0, 0, 0, 0, "Error", 0

# Initialize the Monitor
db_monitor = DatabaseMonitor()

# =============================================================================
# 4. GLOBAL STATE
# =============================================================================
running_pids = {"PROD": None, "DEV": None}
pulse_state = 0

# Data buffers
cpu_history = [0] * 60
ram_history = [0] * 60

# DB Activity Buffers
db_tps_history = [0] * 60
db_read_history = [0] * 60
db_write_history = [0] * 60

is_console_expanded = False
current_browser_path = BACKUP_ROOT 
tick_counter = 0

# UI References
status_indicator_canvas_server = None
status_indicator_text_server = None
status_indicator_canvas_db = None
status_indicator_text_db = None
lbl_db_version = None 

# Card Text Variables
var_card_conns = None
var_card_size = None
var_card_cache = None
var_card_commits = None 

# =============================================================================
# 5. CUSTOM WIDGETS
# =============================================================================
class TelemetryGraph(tk.Canvas):
    def __init__(self, parent, data_source_key, title, color, unit="%", height=150, responsive_height=False, min_y_max=None):
        super().__init__(parent, height=height, bg=THEME['bg_card'], highlightthickness=0)
        self.data_key = data_source_key
        self.line_color = color
        self.title = title
        self.unit = unit
        self.responsive_height = responsive_height
        self.min_y_max = min_y_max 
        
        self.W = 100 
        self.H = height 
        self.current_data = [] 
        
        self.pad_left = 45 
        self.pad_bottom = 20
        self.pad_top = 25
        
        self.bind('<Configure>', self.on_resize)
        self.draw_grid_and_labels(0, 100) 

    def on_resize(self, event):
        self.W = event.width
        if self.responsive_height:
            self.H = event.height
        self.draw_grid_and_labels(0, 100)
        if self.current_data:
            self.update_graph(self.current_data)

    def draw_grid_and_labels(self, min_val, max_val):
        self.delete("grid")
        self.delete("label")
        
        grid_color = '#334155'
        
        # Y-Axis Max Label
        self.create_text(5, self.pad_top, text=f"{max_val:.1f}{self.unit}", anchor='nw', fill=THEME['text_secondary'], font=('Segoe UI', 8), tags="label")
        
        # Y-Axis Min Label
        self.create_text(5, self.H - self.pad_bottom, text="0", anchor='sw', fill=THEME['text_secondary'], font=('Segoe UI', 8), tags="label")
        
        # Title Label
        self.create_text(self.pad_left + 10, 5, text=self.title, anchor='nw', fill=THEME['text_secondary'], font=FONTS['small'], tags="label")
        
        # Current Value Label (Placeholder)
        self.value_text = self.create_text(self.W-10, 5, text=f"0{self.unit}", anchor='ne', fill=self.line_color, font=FONTS['body_bold'], tags="label")
        
        # Grid Lines
        self.create_line(self.pad_left, self.pad_top, self.W, self.pad_top, fill=grid_color, dash=(2, 4), tags="grid")
        mid_y = (self.H - self.pad_bottom + self.pad_top) / 2
        self.create_line(self.pad_left, mid_y, self.W, mid_y, fill=grid_color, dash=(2, 4), tags="grid")
        self.create_line(self.pad_left, self.H - self.pad_bottom, self.W, self.H - self.pad_bottom, fill=THEME['border'], tags="grid")
        
        # X-Axis Time Labels
        self.create_text(self.pad_left, self.H - 2, text="60s ago", anchor='sw', fill=THEME['text_muted'], font=('Segoe UI', 7), tags="label")
        self.create_text(self.W - 5, self.H - 2, text="Now", anchor='se', fill=THEME['text_muted'], font=('Segoe UI', 7), tags="label")

    def update_graph(self, data):
        self.current_data = data
        self.delete("graph_line")
        
        if not data: 
            return
        
        current_val = data[-1]
        max_val = max(data) if max(data) > 0 else 1
        
        # Dynamic Scaling
        if self.unit == "%": 
            display_max = 100
        else: 
            display_max = max_val * 1.2
            if self.min_y_max and display_max < self.min_y_max:
                display_max = self.min_y_max
            
        self.draw_grid_and_labels(0, display_max)
        
        points = []
        n_points = len(data)
        g_w = self.W - self.pad_left
        g_h = self.H - self.pad_bottom - self.pad_top
        step_x = g_w / (n_points - 1) if n_points > 1 else g_w
        
        for i, value in enumerate(data):
            x = self.pad_left + (i * step_x)
            ratio = value / display_max if display_max > 0 else 0
            if ratio > 1: 
                ratio = 1
            y = (self.H - self.pad_bottom) - (ratio * g_h)
            points.extend([x, y])
            
        if len(points) >= 4:
            # Clean Line Graph style
            self.create_line(points, fill=self.line_color, width=3, smooth=True, capstyle='round', tags="graph_line")
            
        # Update Value Label
        if current_val < 10 and self.unit != "%":
             self.itemconfig(self.value_text, text=f"{current_val:.1f}{self.unit}")
        else:
             self.itemconfig(self.value_text, text=f"{current_val:.0f}{self.unit}")
        
        self.tag_raise("label")

# =============================================================================
# 5. CORE FUNCTIONS
# =============================================================================
def log_message(msg, tag='default', timestamp=True):
    try:
        log_box.config(state='normal')
        if timestamp and msg.strip():
            now = datetime.now().strftime("%H:%M:%S")
            log_box.insert(tk.END, f"[{now}] ", 'timestamp')
        log_box.insert(tk.END, f"{msg}\n", tag)
        log_box.see(tk.END)
        log_box.config(state='disabled')
        root.update_idletasks()
    except: 
        pass

def log_status(msg): 
    log_message(msg, tag='status')

def log_error(msg): 
    log_message(msg, tag='error')

def log_raw(msg): 
    log_message(msg, tag='default', timestamp=False)

def clear_console():
    log_box.config(state='normal')
    log_box.delete("1.0", tk.END)
    log_box.insert(tk.END, "\n")
    log_box.config(state='disabled')
    log_status("Console cleared.")

def get_network_details():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except: 
        return "Offline", "N/A", "N/A"

    try:
        proc = subprocess.run("ipconfig", capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
        output = proc.stdout
        mask = "N/A"
        gateway = "N/A"
        adapters = re.split(r'\n\n', output)
        for adapter in adapters:
            if local_ip in adapter:
                mask_match = re.search(r"Subnet Mask[\s\.]*: ([0-9\.]+)", adapter)
                if mask_match: 
                    mask = mask_match.group(1)
                gw_match = re.search(r"Default Gateway.*: (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", adapter)
                if gw_match: 
                    gateway = gw_match.group(1)
                break
        return local_ip, mask, gateway
    except: 
        return local_ip, "N/A", "N/A"

def get_git_info():
    try:
        branch = subprocess.check_output("git rev-parse --abbrev-ref HEAD", shell=True, text=True, creationflags=CREATE_NO_WINDOW).strip()
        status = subprocess.check_output("git status --porcelain", shell=True, text=True, creationflags=CREATE_NO_WINDOW)
        changes = len(status.splitlines())
        last_commit = subprocess.check_output('git log -1 --format="%s (%h)"', shell=True, text=True, creationflags=CREATE_NO_WINDOW).strip()
        return branch, changes, last_commit
    except: 
        return "No Git Repo", 0, "N/A"

def get_db_version():
    if not HAS_PSYCOPG2: 
        return "Driver Missing"
    try:
        conn = psycopg2.connect(dbname="prime_service_portal", user="postgres", host="localhost", port="5432")
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT version();")
        v_str = cur.fetchone()[0]
        conn.close()
        match = re.search(r"PostgreSQL ([\d\.]+)", v_str)
        if match:
            return f"PostgreSQL {match.group(1)}"
        return "PostgreSQL (Unknown)"
    except:
        return "Offline / Unknown"

def update_heartbeat_and_stats():
    """Main Loop."""
    global pulse_state, cpu_history, ram_history, tick_counter
    global db_tps_history, db_read_history, db_write_history
    
    tick_counter += 1
    
    try:
        # 1. Heartbeat
        active_processes = []
        for key, pid in running_pids.items():
            if pid:
                if HAS_PSUTIL and psutil.pid_exists(pid):
                    active_processes.append(f"{key}:{pid}")
                else:
                    running_pids[key] = None
        
        if active_processes:
            pulse_state = (pulse_state + 1) % 20
            b = 0.7 + 0.3 * abs(10 - pulse_state) / 10
            color = f'#{int(16*b):02x}{int(185*b):02x}{int(129*b):02x}'
            txt = f"Active: {', '.join(active_processes)}"
        else:
            color = THEME['status_idle']
            txt = "System Idle"
        
        if status_indicator_canvas_server:
            status_indicator_canvas_server.itemconfig("circle", fill=color, outline=color)
            status_indicator_text_server.set(txt)

        # 2. System Stats
        if HAS_PSUTIL:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
        else:
            cpu = 0; ram = 0
        
        cpu_history.append(cpu); cpu_history.pop(0)
        ram_history.append(ram); ram_history.pop(0)
        
        graph_cpu.update_graph(cpu_history)
        graph_ram.update_graph(ram_history)

        # 3. Database Stats (via Persistent Monitor)
        # Fix: Unpack 8 values (added total_xact)
        conns, tps, reads, writes, size_bytes, cache_ratio, status, total_xact = db_monitor.poll()
        
        if status_indicator_canvas_db:
            if status == "Connected":
                db_color = THEME['status_active']
                db_txt = "DB Connected"
            else:
                db_color = THEME['status_error']
                db_txt = "DB Offline"
            
            status_indicator_canvas_db.itemconfig("circle", fill=db_color, outline=db_color)
            status_indicator_text_db.set(db_txt)

        if status == "Connected":
            # --- CARD UPDATES ---
            if var_card_conns:
                var_card_conns.set(f"{conns} Active")
            
            # Dynamic Size Unit
            if size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024.0:.1f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                size_str = f"{size_bytes / (1024.0*1024.0):.1f} MB"
            else:
                size_str = f"{size_bytes / (1024.0*1024.0*1024.0):.2f} GB"
            
            if var_card_size:
                var_card_size.set(size_str)
                
            if var_card_cache:
                var_card_cache.set(f"{cache_ratio:.1f}%")

            if var_card_commits:
                # Commas for readability
                var_card_commits.set(f"{total_xact:,.0f}")

        # Update History Buffers
        db_tps_history.append(tps); db_tps_history.pop(0)
        db_read_history.append(reads); db_read_history.pop(0)
        db_write_history.append(writes); db_write_history.pop(0)
        
        # Update Graphs
        if 'graph_db_tps' in globals():
            graph_db_tps.update_graph(db_tps_history)
            graph_db_reads.update_graph(db_read_history)
            graph_db_writes.update_graph(db_write_history)

        # 4. Git Stats
        if 'lbl_git_branch' in globals():
            branch, changes, last_commit = get_git_info()
            lbl_git_branch.config(text=f"Branch: {branch}")
            lbl_git_changes.config(text=f"Changes: {changes} uncommitted files")
            lbl_git_commit.config(text=f"Last: {last_commit[:30]}...")

    except Exception as e:
        print(f"Error in update loop: {e}")

    root.after(1000, update_heartbeat_and_stats)

def toggle_console():
    global is_console_expanded
    if not is_console_expanded:
        console_container.pack_forget() 
        console_container.place(x=30, y=130, relwidth=1, width=-60, relheight=1, height=-150)
        console_container.lift() 
        btn_expand.config(text=ICONS['collapse'])
        is_console_expanded = True
    else:
        console_container.place_forget()
        console_container.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        btn_expand.config(text=ICONS['expand'])
        is_console_expanded = False

# =============================================================================
# 6. RECOVERY UI LOGIC
# =============================================================================
def format_date_human(date_obj):
    today = datetime.now().date()
    delta = (today - date_obj).days
    if delta == 0: return "Today"
    elif delta == 1: return "Yesterday"
    else: return date_obj.strftime("%A, %B %d, %Y")

def open_backup_folder(event=None):
    selected_item = backup_tree.selection()
    if selected_item:
        folder_path = backup_tree.item(selected_item[0])['values'][2] 
        if os.path.exists(folder_path): subprocess.run(['explorer', folder_path])

def filter_snapshots(event=None):
    try:
        selected_date = cal.selection_get()
        refresh_recovery_view(filter_date=selected_date)
    except: pass

def refresh_recovery_view(filter_date=None):
    for item in backup_tree.get_children(): backup_tree.delete(item)
    if filter_date is None: 
        if HAS_CALENDAR: cal.calevent_remove('all')
    if not os.path.exists(BACKUP_ROOT): return

    snapshots = []
    for day_folder in os.listdir(BACKUP_ROOT):
        day_path = os.path.join(BACKUP_ROOT, day_folder)
        if os.path.isdir(day_path) and day_folder.startswith("snapshot_"):
            try:
                date_obj = datetime.strptime(day_folder.split('_')[1], '%Y-%m-%d').date()
                if HAS_CALENDAR and filter_date is None: cal.calevent_create(date_obj, "Backup", "backup")
                if filter_date and date_obj != filter_date: continue

                for time_folder in os.listdir(day_path):
                    full_path = os.path.join(day_path, time_folder)
                    if len(time_folder) == 4:
                        time_obj = datetime.strptime(time_folder, "%H%M")
                        fmt_time = time_obj.strftime("%I:%M %p").lstrip("0")
                        fmt_date = format_date_human(date_obj)
                        snapshots.append((fmt_date, fmt_time, full_path, date_obj, time_obj))
            except: continue
    
    snapshots.sort(key=lambda x: (x[3], x[4]), reverse=True)
    for s in snapshots: backup_tree.insert('', 'end', values=(s[0], s[1], s[2]))

def reset_dashboard_view():
    guide_frame.pack_forget()
    browser_frame.pack_forget()
    cal_frame.pack(side='left', fill='both', expand=True, padx=(0, 10), before=right_col)
    list_frame_inner.pack(fill='both', expand=True, padx=20, pady=(0, 20))
    lbl_right_title.config(text="AVAILABLE SNAPSHOTS")

def show_restore_guide():
    cal_frame.pack_forget()
    list_frame_inner.pack_forget()
    browser_frame.pack_forget()
    lbl_right_title.config(text="RESTORE WIZARD (MANUAL MODE)")
    guide_frame.pack(fill='both', expand=True, padx=20, pady=20)

def show_file_browser_root():
    populate_browser(BACKUP_ROOT)
    cal_frame.pack_forget()
    list_frame_inner.pack_forget()
    guide_frame.pack_forget()
    lbl_right_title.config(text="FILE EXPLORER")
    browser_frame.pack(fill='both', expand=True, padx=20, pady=20)

def open_changelog(event=None):
    changelog_path = os.path.join(SCRIPT_DIR, "CHANGELOG_TOOLKIT.md")
    if os.path.exists(changelog_path): subprocess.run(['start', changelog_path], shell=True)

def populate_browser(path):
    global current_browser_path
    current_browser_path = path
    lbl_path.config(text=f"PATH: {path}")
    for item in browser_tree.get_children(): browser_tree.delete(item)
    try:
        items = os.listdir(path)
        folders = sorted([f for f in items if os.path.isdir(os.path.join(path, f))])
        files = sorted([f for f in items if os.path.isfile(os.path.join(path, f))])
        for f in folders:
            full = os.path.join(path, f)
            t = datetime.fromtimestamp(os.path.getmtime(full)).strftime('%Y-%m-%d %I:%M %p')
            browser_tree.insert('', 'end', text=f" {ICONS['folder']}  {f}", values=("Folder", "-", t, full))
        for f in files:
            full = os.path.join(path, f)
            size = f"{os.path.getsize(full) / 1024:.1f} KB"
            t = datetime.fromtimestamp(os.path.getmtime(full)).strftime('%Y-%m-%d %I:%M %p')
            browser_tree.insert('', 'end', text=f" {ICONS['file']}  {f}", values=("File", size, t, full))
    except Exception as e: log_error(f"Error accessing path: {e}")

def browser_navigate(event):
    selected = browser_tree.selection()
    if selected:
        full_path = browser_tree.item(selected[0])['values'][3]
        if os.path.isdir(full_path): populate_browser(full_path)

def browser_up():
    parent = os.path.dirname(current_browser_path)
    if os.path.exists(parent): populate_browser(parent)

def open_file_in_editor(filename):
    path = os.path.join(SCRIPT_DIR, filename)
    if os.path.exists(path): subprocess.run(['start', path], shell=True)
    else: log_error(f"File not found: {filename}")

def open_terminal():
    subprocess.Popen(['start', 'cmd', '/k', r'call venv\Scripts\activate.bat'], shell=True)

def open_python_shell():
    subprocess.Popen(['start', 'cmd', '/k', r'venv\Scripts\python.exe'], shell=True)
    
def open_django_shell():
    # Launches venv activation AND python manage.py shell in one go
    subprocess.Popen(['start', 'cmd', '/k', r'call venv\Scripts\activate.bat && python manage.py shell'], shell=True)

# =============================================================================
# 7. SMART BACKUP ENGINE
# =============================================================================
def run_smart_backup(btn):
    def worker():
        btn.config(state='disabled', bg=THEME['btn_disabled'])
        progress_bar.pack(side='left', fill='x', expand=True, padx=20)
        status_label.pack(side='left', padx=(0, 20))
        status_label.config(text="Initializing...", fg=THEME['text_secondary'])
        progress_bar['value'] = 0
        try:
            now = datetime.now()
            dest_day = os.path.join(BACKUP_ROOT, f"snapshot_{now.strftime('%Y-%m-%d')}")
            dest_time = os.path.join(dest_day, now.strftime('%H%M'))
            dest_proj = os.path.join(dest_time, "prime_service_portal")
            dest_config = os.path.join(dest_time, "_config")
            
            os.makedirs(dest_proj, exist_ok=True)
            os.makedirs(dest_config, exist_ok=True)

            root.after(0, lambda: update_ui(5, "Generating requirements.txt..."))
            subprocess.run("pip freeze > requirements.txt", shell=True, creationflags=CREATE_NO_WINDOW)
            
            appdata = os.getenv('APPDATA')
            pgpass_src = os.path.join(appdata, 'postgresql', 'pgpass.conf')
            if os.path.exists(pgpass_src): shutil.copy2(pgpass_src, os.path.join(dest_config, "pgpass.conf"))
            
            root.after(0, lambda: update_ui(10, "Scanning files..."))
            file_list = []
            for root_dir, dirs, files in os.walk(SCRIPT_DIR):
                if 'venv' in dirs: dirs.remove('venv')
                if '.git' in dirs: dirs.remove('.git')
                if '__pycache__' in dirs: dirs.remove('__pycache__')
                for file in files:
                    src_file = os.path.join(root_dir, file)
                    rel_path = os.path.relpath(src_file, SCRIPT_DIR)
                    file_list.append((src_file, rel_path))
            
            total_files = len(file_list)
            for i, (src, rel) in enumerate(file_list):
                percent = 10 + (i / total_files) * 80
                dest = os.path.join(dest_proj, rel)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(src, dest)
                if i % 10 == 0: root.after(0, lambda p=percent, m=f"Copying: {rel[:30]}...": update_ui(p, m))
            
            root.after(0, lambda: update_ui(90, "Exporting Database..."))
            db_file = os.path.join(dest_time, "portal_db.sql")
            subprocess.run(f'pg_dump -U postgres prime_service_portal > "{db_file}"', shell=True, creationflags=CREATE_NO_WINDOW)
            
            root.after(0, lambda: update_ui(100, "Done!"))
            time.sleep(0.5)
            log_status(f"Snapshot Complete: {len(file_list)} files + DB")
            root.after(0, reset_ui_success)
        except Exception as e:
            log_error(f"BACKUP FAILED: {str(e)}")
            root.after(0, reset_ui_error)

    def update_ui(val, text):
        progress_bar['value'] = val
        status_label.config(text=text, fg=THEME['text_secondary'])

    def reset_ui_success():
        progress_bar.pack_forget()
        status_label.config(text="✔ Snapshot Complete", fg=THEME['status_active'])
        btn.config(state='normal', bg=THEME['btn_backup'])
        refresh_recovery_view()
        root.after(3000, lambda: status_label.pack_forget())

    def reset_ui_error():
        progress_bar.pack_forget()
        status_label.config(text="Failed", fg=THEME['status_error'])
        btn.config(state='normal', bg=THEME['btn_backup'])

    threading.Thread(target=worker, daemon=True).start()

# =============================================================================
# 8. COMMAND HANDLERS
# =============================================================================
def run_command_with_log(cmd, label):
    def task():
        log_raw(""); log_status(f"STARTING: {label}"); log_raw("-" * 50)
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True, creationflags=CREATE_NO_WINDOW)
            for line in iter(p.stdout.readline, ''): log_raw(line.rstrip())
            p.wait(); log_raw("-" * 50); log_status(f"COMPLETED: {label}")
        except Exception as e: log_error(f"ERROR: {str(e)}")
    threading.Thread(target=task, daemon=True).start()

def run_smart_git_push():
    summary = simpledialog.askstring("Commit & Push", "Enter commit message:", parent=root)
    if not summary: return
    
    def task():
        log_raw("")
        log_status("STARTING: SMART COMMIT & PUSH")
        log_raw("-" * 50)
        
        try:
            # 1. Add
            log_raw(">> git add .")
            subprocess.run("git add .", shell=True, check=True, creationflags=CREATE_NO_WINDOW)
            
            # 2. Commit
            log_raw(f">> git commit -m \"{summary}\"")
            proc_commit = subprocess.run(f'git commit -m "{summary}"', shell=True, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
            log_raw(proc_commit.stdout)

            # 3. Push (EXTERNAL WINDOW + VENV ACTIVATION for Credential Inheritance)
            log_raw(">> git push (Launching auth window...)")
            
            # CRITICAL FIX: We launch 'activate.bat' BEFORE 'git push' inside the new CMD window.
            # This replicates the "Green Window" environment where auth works.
            cmd_str = (
                'start "Git Push" cmd /c '
                '"call venv\\Scripts\\activate.bat && echo. && echo --------------------------- && '
                'echo   EXECUTING GIT PUSH... && echo --------------------------- && echo. && '
                'git push && (echo. & echo [SUCCESS] Closing in 5 seconds... & timeout /t 5) || (echo. & echo [FAILED] Review error above. & pause)"'
            )
            subprocess.run(cmd_str, shell=True)
            
            log_status("External Push Process Launched.")
            log_raw("Please check the popup window for final status.")

        except Exception as e:
            log_error(f"GIT ERROR: {str(e)}")
            
    threading.Thread(target=task, daemon=True).start()

def run_server(cmd, key, btn_start, btn_stop):
    def task():
        try:
            log_raw(""); log_status(f"{ICONS['rocket']} Initializing {key} server...")
            btn_start.config(state='disabled', bg=THEME['btn_disabled']); btn_stop.config(state='normal', bg=THEME['btn_danger'])
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True, bufsize=1, universal_newlines=True, creationflags=CREATE_NO_WINDOW)
            running_pids[key] = p.pid
            for line in iter(p.stdout.readline, ''):
                if "GET /service-desk/notifications/poll/" in line: continue
                log_raw(line.rstrip())
            p.wait()
        except Exception as e: log_error(f"SERVER ERROR: {str(e)}")
        finally: running_pids[key] = None; btn_start.config(state='normal', bg=btn_start.original_bg); btn_stop.config(state='disabled', bg=THEME['btn_secondary'])
    threading.Thread(target=task, daemon=True).start()

def stop_server(key):
    pid = running_pids.get(key)
    if pid: subprocess.run(f"taskkill /F /T /PID {pid}", shell=True, creationflags=CREATE_NO_WINDOW); running_pids[key] = None; log_status(f"{ICONS['stop']} {key} server stopped.")

def run_script_command(script_name, label): run_command_with_log(f"venv\\Scripts\\python.exe {script_name}", label)
def wipe_database_confirm():
    if messagebox.askyesno("Confirm Wipe", "PERMANENTLY DELETE ALL DATA?\nCannot be undone."): run_script_command("wipe_inventory.py", "WIPE INVENTORY")
def refresh_demo_data_confirm():
    if messagebox.askyesno("Confirm Refresh", "Reset all data to Demo State?"): run_command_with_log("python manage.py rebuild_demo_data", "REBUILD DEMO")
def open_url(url): webbrowser.open(url)
def open_explorer(path): subprocess.run(['explorer', path])
def open_terminal(): subprocess.Popen(['start', 'cmd', '/k', r'call venv\Scripts\activate.bat'], shell=True)
def open_python_shell(): subprocess.Popen(['start', 'cmd', '/k', r'venv\Scripts\python.exe'], shell=True)


# =============================================================================
# 9. UI HELPERS (FACTORIES)
# =============================================================================
def create_hero_card(parent, title, subtitle, icon, btn_configs):
    card = tk.Frame(parent, bg=THEME['bg_card'], bd=0)
    card.pack(side='left', fill='both', expand=True, padx=(0, 10), pady=0)
    header = tk.Frame(card, bg=THEME['bg_card']); header.pack(fill='x', padx=20, pady=(20, 10))
    tk.Label(header, text=icon, font=('Segoe UI', 26), fg=THEME['accent_blue'], bg=THEME['bg_card']).pack(side='left', padx=(0, 15))
    meta = tk.Frame(header, bg=THEME['bg_card']); meta.pack(side='left', fill='x')
    tk.Label(meta, text=title, font=FONTS['subheader'], fg=THEME['text_primary'], bg=THEME['bg_card']).pack(anchor='w')
    tk.Label(meta, text=subtitle, font=FONTS['small'], fg=THEME['text_secondary'], bg=THEME['bg_card']).pack(anchor='w')
    tk.Frame(card, bg=THEME['border'], height=1).pack(fill='x', padx=20, pady=10)
    btn_frame = tk.Frame(card, bg=THEME['bg_card']); btn_frame.pack(fill='x', padx=20, pady=(0, 20))
    created_btns = []
    for cfg in btn_configs:
        btn = tk.Button(btn_frame, text=f"{cfg.get('icon','')} {cfg['text']}", command=cfg['command'], bg=cfg['color'], fg='white', font=FONTS['button'], bd=0, padx=15, pady=8, cursor='hand2', activebackground=cfg['color'])
        btn.original_bg = cfg['color']; btn.pack(fill='x', pady=(0, 5)); created_btns.append(btn)
    return card, created_btns

def create_action_button(parent, text, command, color, icon=''):
    btn = tk.Button(parent, text=f"{icon} {text}" if icon else text, command=command, bg=color, fg='white', font=FONTS['button'], bd=0, padx=16, pady=10, cursor='hand2', activebackground=color)
    return btn

def create_ghost_btn(parent, icon, text, cmd):
    btn_frame = tk.Frame(parent, bg=THEME['bg_primary'], cursor='hand2'); btn_frame.pack(side='left', padx=15)
    def on_enter(e): l_icon.config(fg='white'); l_text.config(fg='white')
    def on_leave(e): l_icon.config(fg=THEME['accent_blue']); l_text.config(fg=THEME['accent_blue'])
    def on_click(e): cmd()
    l_icon = tk.Label(btn_frame, text=icon, font=('Segoe UI', 14), fg=THEME['accent_blue'], bg=THEME['bg_primary'], cursor='hand2'); l_icon.pack(side='left', padx=(0, 6))
    l_text = tk.Label(btn_frame, text=text, font=('Segoe UI', 10, 'bold'), fg=THEME['accent_blue'], bg=THEME['bg_primary'], cursor='hand2'); l_text.pack(side='left', pady=(8, 0))
    for w in [btn_frame, l_icon, l_text]: w.bind('<Enter>', on_enter); w.bind('<Leave>', on_leave); w.bind('<Button-1>', on_click)
    return btn_frame

def create_status_badge(parent, text_var):
    box = tk.Frame(parent, bg=THEME['bg_card'], highlightbackground=THEME['border'], highlightthickness=1)
    inner = tk.Frame(box, bg=THEME['bg_card']); inner.pack(padx=15, pady=8)
    canvas = tk.Canvas(inner, width=12, height=12, bg=THEME['bg_card'], highlightthickness=0)
    canvas.pack(side='left', padx=(0,8))
    canvas.create_oval(2,2,10,10, fill=THEME['status_idle'], outline="", tags="circle")
    tk.Label(inner, textvariable=text_var, font=FONTS['body_bold'], fg=THEME['text_primary'], bg=THEME['bg_card']).pack(side='left')
    return box, canvas

def create_metric_card(parent, title, value_var, accent_color):
    """Creates a Status Card with a colored accent bar."""
    card = tk.Frame(parent, bg=THEME['bg_card'], highlightthickness=0)
    bar = tk.Frame(card, bg=accent_color, width=5)
    bar.pack(side='left', fill='y')
    content = tk.Frame(card, bg=THEME['bg_card'], padx=20, pady=15)
    content.pack(side='left', fill='both', expand=True)
    tk.Label(content, text=title.upper(), font=FONTS['small'], fg=THEME['text_secondary'], bg=THEME['bg_card']).pack(anchor='w')
    if value_var:
        tk.Label(content, textvariable=value_var, font=FONTS['big_value'], fg=THEME['text_primary'], bg=THEME['bg_card']).pack(anchor='w', pady=(5, 0))
    else:
        tk.Label(content, text="--", font=FONTS['big_value'], fg=THEME['text_primary'], bg=THEME['bg_card']).pack(anchor='w', pady=(5, 0))
    return card

# =============================================================================
# 10. MAIN UI SETUP
# =============================================================================
root = tk.Tk()
root.title("PRIME Service Portal - Developer Toolkit v6.30")

# Work Area Centering
wa_left, wa_top, wa_right, wa_bottom = get_work_area()
W_WIDTH, W_HEIGHT = 1200, 900
x_pos = wa_left + (wa_right - wa_left - W_WIDTH) // 2
y_pos = wa_top + (wa_bottom - wa_top - W_HEIGHT) // 2
root.geometry(f'{W_WIDTH}x{W_HEIGHT}+{x_pos}+{y_pos}')
root.configure(bg=THEME['bg_primary'])

# --- HEADER ---
header = tk.Frame(root, bg=THEME['bg_primary'], height=90); header.pack(fill='x', padx=30, pady=(20, 0)); header.pack_propagate(False)
h_left = tk.Frame(header, bg=THEME['bg_primary']); h_left.pack(side='left', fill='y')
try:
    if HAS_PIL:
        logo_path = os.path.join(SCRIPT_DIR, "static/images/logo_white.png")
        if os.path.exists(logo_path):
            original_img = Image.open(logo_path)
            target_height = 65 
            aspect_ratio = original_img.width / original_img.height
            target_width = int(target_height * aspect_ratio)
            resized_img = original_img.resize((target_width, target_height), Image.LANCZOS)
            logo_img = ImageTk.PhotoImage(resized_img); logo_label = tk.Label(h_left, image=logo_img, bg=THEME['bg_primary']); logo_label.image = logo_img; logo_label.pack(side='left', padx=(0,20))
        else: tk.Label(h_left, text="PRIME AE", font=('Arial', 24, 'bold'), fg='white', bg=THEME['bg_primary']).pack(side='left')
    else: tk.Label(h_left, text="PRIME AE", font=('Arial', 24, 'bold'), fg='white', bg=THEME['bg_primary']).pack(side='left')
except: tk.Label(h_left, text="PRIME AE", font=('Arial', 24, 'bold'), fg='white', bg=THEME['bg_primary']).pack(side='left')
tk.Frame(h_left, bg=THEME['border'], width=2).pack(side='left', fill='y', padx=(0, 20))
h_titles = tk.Frame(h_left, bg=THEME['bg_primary']); h_titles.pack(side='left')
tk.Label(h_titles, text="DEVELOPER TOOLKIT", font=FONTS['header'], fg=THEME['accent_blue'], bg=THEME['bg_primary']).pack(anchor='w')
version_lbl = tk.Label(h_titles, text="v6.30 | Django 5.2 | PostgreSQL 18", font=FONTS['small'], fg=THEME['text_secondary'], bg=THEME['bg_primary'], cursor="hand2")
version_lbl.pack(anchor='w'); version_lbl.bind("<Button-1>", open_changelog)
tk.Label(h_titles, text="© 2025 | Conceived & Designed by Richard Haynes", font=('Segoe UI', 8), fg=THEME['text_muted'], bg=THEME['bg_primary']).pack(anchor='w', pady=(2,0))
h_right = tk.Frame(header, bg=THEME['bg_primary']); h_right.pack(side='right', fill='y')
dock_row = tk.Frame(h_right, bg=THEME['bg_primary']); dock_row.pack(side='top', anchor='e', pady=(5, 0))
create_ghost_btn(dock_row, ICONS['globe'], "PORTAL", lambda: open_url("http://127.0.0.1:8000"))
create_ghost_btn(dock_row, ICONS['shield'], "ADMIN", lambda: open_url("http://127.0.0.1:8000/admin"))
create_ghost_btn(dock_row, ICONS['folder'], "PROJECT", lambda: open_explorer(SCRIPT_DIR))
ctx_row = tk.Frame(h_right, bg=THEME['bg_primary']); ctx_row.pack(side='top', anchor='e', pady=(2, 0))
tk.Label(ctx_row, text=f"User: {getpass.getuser()} | Host: {socket.gethostname()}", font=('Segoe UI', 10), fg=THEME['text_secondary'], bg=THEME['bg_primary']).pack(anchor='e', padx=15)
ip, mask, gw = get_network_details()
net_row = tk.Frame(h_right, bg=THEME['bg_primary']); net_row.pack(side='top', anchor='e', pady=(2, 0))
tk.Label(net_row, text=f"IPv4: {ip} | Mask: {mask} | Gwy: {gw}", font=('Segoe UI', 8), fg=THEME['text_muted'], bg=THEME['bg_primary']).pack(anchor='e', padx=15)

# --- NOTEBOOK TABS ---
style = ttk.Style(); style.theme_use('default')
style.layout('Seamless.TNotebook.Tab', [('Notebook.tab', {'sticky': 'nswe', 'children': [('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children': [('Notebook.label', {'side': 'top', 'sticky': ''})]})]})])
style.configure('Seamless.TNotebook', background=THEME['bg_primary'], borderwidth=0)
style.configure('Seamless.TNotebook.Tab', background=THEME['bg_primary'], foreground=THEME['text_secondary'], font=FONTS['body_bold'], padding=[20, 15], borderwidth=0)
style.map('Seamless.TNotebook.Tab', background=[('selected', THEME['bg_primary'])], foreground=[('selected', THEME['accent_blue'])])
notebook = ttk.Notebook(root, style='Seamless.TNotebook'); notebook.pack(fill='both', expand=True, padx=30, pady=(20, 0))

# =============================================================================
# TAB 1: SERVER CONTROL
# =============================================================================
tab_server = tk.Frame(notebook, bg=THEME['bg_primary']); notebook.add(tab_server, text=f"{ICONS['rocket']} SERVER CONTROL")
status_strip = tk.Frame(tab_server, bg=THEME['bg_primary']); status_strip.pack(fill='x', padx=5, pady=(5, 5))
status_indicator_text_server = tk.StringVar(value="Idle")
status_box_server, status_indicator_canvas_server = create_status_badge(status_strip, status_indicator_text_server)
status_box_server.pack(side='right')
tk.Label(status_strip, text="PROCESS MANAGEMENT", font=FONTS['small'], fg=THEME['text_secondary'], bg=THEME['bg_primary']).pack(side='left', anchor='s', pady=10)
ctrl_frame = tk.Frame(tab_server, bg=THEME['bg_primary']); ctrl_frame.pack(fill='x', pady=(0, 10))
prod_c, prod_btns = create_hero_card(ctrl_frame, "Production Server", "Waitress WSGI | Enterprise", ICONS['shield'], [{'text': 'START SERVER', 'command': None, 'color': THEME['btn_success'], 'icon': ICONS['play']}, {'text': 'STOP', 'command': lambda: stop_server("PROD"), 'color': THEME['btn_danger'], 'icon': ICONS['stop']}])
prod_btns[0].config(command=lambda: run_server("python run_production.py", "PROD", prod_btns[0], prod_btns[1])); prod_btns[1].config(state='disabled', bg=THEME['btn_secondary'])
dev_c, dev_btns = create_hero_card(ctrl_frame, "Development Server", "Django Runserver | Debug", ICONS['lightning'], [{'text': 'START SERVER', 'command': None, 'color': THEME['btn_info'], 'icon': ICONS['play']}, {'text': 'STOP', 'command': lambda: stop_server("DEV"), 'color': THEME['btn_danger'], 'icon': ICONS['stop']}])
dev_btns[0].config(command=lambda: run_server("python manage.py runserver", "DEV", dev_btns[0], dev_btns[1])); dev_btns[1].config(state='disabled', bg=THEME['btn_secondary']); dev_c.pack_configure(padx=0)
graph_frame = tk.Frame(tab_server, bg=THEME['bg_primary']); graph_frame.pack(fill='both', expand=True, pady=(0, 20))
tk.Label(graph_frame, text=f"{ICONS['gear']} SYSTEM TELEMETRY (LIVE)", font=FONTS['small'], fg=THEME['text_secondary'], bg=THEME['bg_primary']).pack(anchor='w', pady=(10, 5))
g_container = tk.Frame(graph_frame, bg=THEME['bg_primary']); g_container.pack(fill='both', expand=True)
graph_cpu = TelemetryGraph(g_container, data_source_key='cpu', title=f"{ICONS['cpu']} CPU USAGE HISTORY", color=THEME['accent_blue'], unit="%", height=150, responsive_height=False); graph_cpu.pack(side='left', fill='both', expand=True, padx=(0, 10))
graph_ram = TelemetryGraph(g_container, data_source_key='ram', title=f"{ICONS['ram']} MEMORY USAGE HISTORY", color='#a78bfa', unit="%", height=150, responsive_height=False); graph_ram.pack(side='left', fill='both', expand=True)

# =============================================================================
# TAB 2: DATABASE OPS
# =============================================================================
tab_db = tk.Frame(notebook, bg=THEME['bg_primary']); notebook.add(tab_db, text=f"{ICONS['database']} DATABASE OPS")
db_grid = tk.Frame(tab_db, bg=THEME['bg_primary']); db_grid.pack(fill='both', expand=True, pady=20)
db_top = tk.Frame(db_grid, bg=THEME['bg_primary']); db_top.pack(fill='x', pady=(0, 20))
tk.Label(db_top, text="MAINTENANCE TASKS", font=FONTS['body_bold'], fg=THEME['text_secondary'], bg=THEME['bg_primary']).pack(anchor='w', pady=(0,5))
db_actions = tk.Frame(db_top, bg=THEME['bg_card']); db_actions.pack(fill='x', ipady=10)
create_action_button(db_actions, "RUN MIGRATIONS", lambda: run_command_with_log("python manage.py migrate", "MIGRATE"), THEME['btn_purple'], ICONS['refresh']).pack(side='left', padx=20)
create_action_button(db_actions, "REFRESH DEMO", refresh_demo_data_confirm, THEME['btn_success'], ICONS['refresh']).pack(side='left')
create_action_button(db_actions, "WIPE INVENTORY DB", wipe_database_confirm, THEME['btn_danger'], ICONS['trash']).pack(side='right', padx=20)
create_action_button(db_actions, "POPULATE DATA", lambda: run_script_command("populate_inventory.py", "SEED"), THEME['btn_info'], ICONS['seed']).pack(side='right')
cards_frame = tk.Frame(db_grid, bg=THEME['bg_primary']); cards_frame.pack(fill='x', pady=(0, 20))
var_card_conns = tk.StringVar(value="-- Active"); card_conns = create_metric_card(cards_frame, "Active Sessions", var_card_conns, THEME['accent_blue']); card_conns.pack(side='left', fill='x', expand=True, padx=(0, 10))
var_card_size = tk.StringVar(value="-- MB"); card_size = create_metric_card(cards_frame, "Database Size", var_card_size, THEME['status_active']); card_size.pack(side='left', fill='x', expand=True, padx=(0, 10))
var_card_cache = tk.StringVar(value="-- %"); card_cache = create_metric_card(cards_frame, "Cache Hit Ratio", var_card_cache, THEME['accent_purple']); card_cache.pack(side='left', fill='x', expand=True, padx=(0, 10))
var_card_commits = tk.StringVar(value="--"); card_commits = create_metric_card(cards_frame, "Total Commits", var_card_commits, THEME['accent_yellow']); card_commits.pack(side='left', fill='x', expand=True)
db_graphs = tk.Frame(db_grid, bg=THEME['bg_primary']); db_graphs.pack(fill='both', expand=True)
graph_db_tps = TelemetryGraph(db_graphs, data_source_key='db_tps', title="TRANSACTIONS / SEC", color=THEME['accent_orange'], unit="", responsive_height=True, min_y_max=1.0); graph_db_tps.pack(side='left', fill='both', expand=True, padx=(0, 10))
graph_db_reads = TelemetryGraph(db_graphs, data_source_key='db_reads', title="READS / SEC (TUPLES FETCHED)", color=THEME['accent_blue'], unit="", responsive_height=True, min_y_max=10.0); graph_db_reads.pack(side='left', fill='both', expand=True, padx=(0, 10))
graph_db_writes = TelemetryGraph(db_graphs, data_source_key='db_writes', title="WRITES / SEC (INSERT/UPD/DEL)", color=THEME['accent_pink'], unit="", responsive_height=True, min_y_max=1.0); graph_db_writes.pack(side='left', fill='both', expand=True)

# TAB 3: DEV TOOLS
tab_dev = tk.Frame(notebook, bg=THEME['bg_primary']); notebook.add(tab_dev, text=f"{ICONS['terminal']} DEV TOOLS")
dev_grid = tk.Frame(tab_dev, bg=THEME['bg_primary']); dev_grid.pack(fill='both', expand=True, pady=20)
dev_top = tk.Frame(dev_grid, bg=THEME['bg_primary']); dev_top.pack(fill='x', pady=(0, 20))
tk.Label(dev_top, text="COMMAND CENTER", font=FONTS['body_bold'], fg=THEME['text_secondary'], bg=THEME['bg_primary']).pack(anchor='w', pady=(0,5))
dev_actions = tk.Frame(dev_top, bg=THEME['bg_card']); dev_actions.pack(fill='x', ipady=10)
create_action_button(dev_actions, "TERMINAL", open_terminal, THEME['btn_secondary'], ICONS['terminal']).pack(side='left', padx=20)
create_action_button(dev_actions, "PYTHON SHELL", open_python_shell, THEME['btn_secondary'], ICONS['python']).pack(side='left')
# NEW BUTTON: Django Shell
create_action_button(dev_actions, "DJANGO SHELL", open_django_shell, THEME['btn_secondary'], ICONS['django']).pack(side='left', padx=20)
create_action_button(dev_actions, "COLLECT STATIC", lambda: run_command_with_log("python manage.py collectstatic --noinput", "STATIC"), THEME['btn_info'], ICONS['folder']).pack(side='left')
# UPDATED BUTTON: Commit & Push
create_action_button(dev_actions, "COMMIT & PUSH", run_smart_git_push, THEME['accent_orange'], ICONS['git']).pack(side='left', padx=20)

dev_mid = tk.Frame(dev_grid, bg=THEME['bg_primary']); dev_mid.pack(fill='both', expand=True)
lbl_git_branch = tk.Label(None); lbl_git_changes = tk.Label(None); lbl_git_commit = tk.Label(None)
git_card = tk.Frame(dev_mid, bg=THEME['bg_card'], padx=20, pady=20); git_card.pack(side='left', fill='both', expand=True, padx=(0, 10))
tk.Label(git_card, text=f"{ICONS['git']} SOURCE CONTROL", font=FONTS['body_bold'], fg=THEME['text_secondary'], bg=THEME['bg_card']).pack(anchor='w', pady=(0, 10))
# ADDED REPO INFO
tk.Label(git_card, text="Repo: richardlhaynes-rgb", font=FONTS['small'], fg=THEME['accent_blue'], bg=THEME['bg_card']).pack(anchor='w', pady=(0, 5))
lbl_git_branch = tk.Label(git_card, text="Branch: Loading...", font=FONTS['title'], fg=THEME['accent_orange'], bg=THEME['bg_card']); lbl_git_branch.pack(anchor='w')
lbl_git_changes = tk.Label(git_card, text="Changes: ...", font=FONTS['small'], fg=THEME['text_primary'], bg=THEME['bg_card']); lbl_git_changes.pack(anchor='w', pady=(5,0))
lbl_git_commit = tk.Label(git_card, text="Last: ...", font=FONTS['small'], fg=THEME['text_muted'], bg=THEME['bg_card']); lbl_git_commit.pack(anchor='w')

env_card = tk.Frame(dev_mid, bg=THEME['bg_card'], padx=20, pady=20); env_card.pack(side='left', fill='both', expand=True, padx=(0, 10))
tk.Label(env_card, text=f"{ICONS['code']} ENVIRONMENT", font=FONTS['body_bold'], fg=THEME['text_secondary'], bg=THEME['bg_card']).pack(anchor='w', pady=(0, 10))
tk.Label(env_card, text=f"Python: {sys.version.split()[0]}", font=FONTS['small'], fg=THEME['text_primary'], bg=THEME['bg_card']).pack(anchor='w')
tk.Label(env_card, text="Django: 5.2", font=FONTS['small'], fg=THEME['text_primary'], bg=THEME['bg_card']).pack(anchor='w', pady=(5,0))
tk.Label(env_card, text="Venv: Active", font=FONTS['small'], fg=THEME['status_active'], bg=THEME['bg_card']).pack(anchor='w', pady=(5,0))
quick_card = tk.Frame(dev_mid, bg=THEME['bg_card'], padx=20, pady=20); quick_card.pack(side='left', fill='both', expand=True)
tk.Label(quick_card, text=f"{ICONS['link']} QUICK EDIT", font=FONTS['body_bold'], fg=THEME['text_secondary'], bg=THEME['bg_card']).pack(anchor='w', pady=(0, 10))
tk.Button(quick_card, text="settings.py", command=lambda: open_file_in_editor("prime_service_portal/settings.py"), bg=THEME['bg_primary'], fg=THEME['accent_blue'], bd=0, padx=10).pack(fill='x', pady=2)
tk.Button(quick_card, text="urls.py", command=lambda: open_file_in_editor("prime_service_portal/urls.py"), bg=THEME['bg_primary'], fg=THEME['accent_blue'], bd=0, padx=10).pack(fill='x', pady=2)
tk.Button(quick_card, text="models.py", command=lambda: open_file_in_editor("inventory/models.py"), bg=THEME['bg_primary'], fg=THEME['accent_blue'], bd=0, padx=10).pack(fill='x', pady=2)

# TAB 4: RECOVERY
tab_rec = tk.Frame(notebook, bg=THEME['bg_primary']); notebook.add(tab_rec, text=f"{ICONS['shield']} RECOVERY")
r_tools = tk.Frame(tab_rec, bg=THEME['bg_primary']); r_tools.pack(fill='x', padx=5, pady=(10, 5))
r_t_box = tk.Frame(r_tools, bg=THEME['bg_card']); r_t_box.pack(fill='x', pady=5, ipady=10)
btn_snap = create_action_button(r_t_box, "TAKE SNAPSHOT", None, THEME['btn_backup'], ICONS['shield']); btn_snap.config(command=lambda: run_smart_backup(btn_snap)); btn_snap.pack(side='left', padx=20)
create_action_button(r_t_box, "RESTORE", show_restore_guide, THEME['btn_purple'], ICONS['refresh']).pack(side='left')
create_action_button(r_t_box, "EXPLORE ROOT", show_file_browser_root, THEME['btn_secondary'], ICONS['folder']).pack(side='left', padx=20)
progress_frame = tk.Frame(r_t_box, bg=THEME['bg_card']); status_label = tk.Label(r_t_box, text="Ready", font=FONTS['small'], fg=THEME['text_secondary'], bg=THEME['bg_card'])
style.configure("green.Horizontal.TProgressbar", foreground=THEME['status_active'], background=THEME['status_active'])
progress_bar = ttk.Progressbar(r_t_box, style="green.Horizontal.TProgressbar", mode='determinate', length=200)
rec_dash = tk.Frame(tab_rec, bg=THEME['bg_primary']); rec_dash.pack(fill='both', expand=True, padx=5, pady=(5, 20))
cal_frame = tk.Frame(rec_dash, bg=THEME['bg_card']); cal_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
tk.Label(cal_frame, text="SNAPSHOT HISTORY", font=FONTS['body_bold'], fg=THEME['text_secondary'], bg=THEME['bg_card']).pack(pady=10)
if HAS_CALENDAR:
    cal = Calendar(cal_frame, selectmode='day', background=THEME['bg_primary'], foreground=THEME['text_primary'], headersbackground=THEME['accent_blue'], normalbackground=THEME['bg_card'], borderwidth=0); cal.pack(pady=10, padx=20, fill='both', expand=True); cal.tag_config("backup", background=THEME['accent_blue'], foreground='white'); cal.bind("<<CalendarSelected>>", filter_snapshots)
else:
    cal_placeholder = tk.Label(cal_frame, text="(Calendar Module Missing)\nRun: pip install tkcalendar", bg=THEME['bg_card'], fg=THEME['status_warning'], font=FONTS['small']); cal_placeholder.pack(fill='both', expand=True, pady=20)
right_col = tk.Frame(rec_dash, bg=THEME['bg_card']); right_col.pack(side='left', fill='both', expand=True)
lbl_right_title = tk.Label(right_col, text="AVAILABLE SNAPSHOTS", font=FONTS['body_bold'], fg=THEME['text_secondary'], bg=THEME['bg_card']); lbl_right_title.pack(pady=10)
list_frame_inner = tk.Frame(right_col, bg=THEME['bg_card']); list_frame_inner.pack(fill='both', expand=True, padx=20, pady=(0, 20))
tree_scroll = ttk.Scrollbar(list_frame_inner); tree_scroll.pack(side='right', fill='y')
style.configure("Treeview", background=THEME['bg_primary'], foreground=THEME['text_primary'], fieldbackground=THEME['bg_primary'], borderwidth=0)
style.configure("Treeview.Heading", background=THEME['bg_card'], foreground=THEME['text_secondary'], font=FONTS['body_bold'])
backup_tree = ttk.Treeview(list_frame_inner, columns=("Date", "Time"), show='headings', yscrollcommand=tree_scroll.set)
backup_tree.heading("Date", text="Date"); backup_tree.heading("Time", text="Eastern Time (US & Canada)"); backup_tree.column("Date", width=200, anchor='center'); backup_tree.column("Time", width=180, anchor='center'); backup_tree.pack(side='left', fill='both', expand=True)
tree_scroll.config(command=backup_tree.yview); backup_tree.bind("<Double-1>", open_backup_folder)
guide_frame = tk.Frame(right_col, bg=THEME['bg_primary'])
guide_text = scrolledtext.ScrolledText(guide_frame, bg=THEME['bg_primary'], fg=THEME['text_primary'], font=('Segoe UI', 10), bd=0, padx=20, pady=20); guide_text.pack(fill='both', expand=True)
guide_text.insert(tk.END, """RESTORE INSTRUCTIONS (MANUAL)\n\n1. LOCATE SNAPSHOT:\n   - Select the snapshot folder from the list.\n   - Copy the 'prime_service_portal' folder inside it.\n\n2. REPLACE PROJECT:\n   - Go to C:\\Projects.\n   - Delete or rename the existing 'prime_service_portal' folder.\n   - Paste the new folder here.\n\n3. REBUILD ENVIRONMENT:\n   - Open Terminal in C:\\Projects\\prime_service_portal.\n   - Run: python -m venv venv\n   - Run: venv\\Scripts\\activate\n   - Run: pip install -r requirements.txt\n\n4. RESTORE DATABASE:\n   - Open pgAdmin 4.\n   - Right-click 'prime_service_portal' DB > Restore.\n   - Select the 'portal_db.sql' file from your snapshot folder.\n\n5. RESTORE CONFIG:\n   - Copy 'pgpass.conf' from the snapshot's '_config' folder.\n   - Paste it into %APPDATA%\\postgresql\\"""); guide_text.config(state='disabled')
tk.Button(guide_frame, text="BACK TO SNAPSHOTS", command=reset_dashboard_view, bg=THEME['btn_secondary'], fg='white', font=FONTS['button'], bd=0, pady=10).pack(fill='x', pady=(10, 0))
browser_frame = tk.Frame(right_col, bg=THEME['bg_primary'])
b_nav = tk.Frame(browser_frame, bg=THEME['bg_card']); b_nav.pack(fill='x')
tk.Button(b_nav, text=f"{ICONS['back']} UP LEVEL", command=browser_up, bg=THEME['btn_info'], fg='white', font=FONTS['button'], bd=0).pack(side='left', padx=10, pady=10)
lbl_path = tk.Label(b_nav, text="PATH:", font=FONTS['small'], fg=THEME['text_secondary'], bg=THEME['bg_card']); lbl_path.pack(side='left', padx=10)
browser_tree = ttk.Treeview(browser_frame, columns=("Type", "Size", "Modified", "Path"), displaycolumns=("Type", "Size", "Modified"), yscrollcommand=tree_scroll.set)
browser_tree.heading("#0", text="Name", anchor='w'); browser_tree.heading("Type", text="Type"); browser_tree.heading("Size", text="Size"); browser_tree.heading("Modified", text="Date Modified"); browser_tree.column("#0", width=250); browser_tree.column("Type", width=80, anchor='center'); browser_tree.column("Size", width=80, anchor='e'); browser_tree.column("Modified", width=150, anchor='center')
browser_tree.pack(fill='both', expand=True, pady=(10, 0)); browser_tree.bind("<Double-1>", browser_navigate)
tk.Button(browser_frame, text="CLOSE EXPLORER", command=reset_dashboard_view, bg=THEME['btn_secondary'], fg='white', font=FONTS['button'], bd=0, pady=10).pack(fill='x', pady=(10, 0))

# --- CONSOLE ---
console_container = tk.Frame(root, bg=THEME['bg_primary']); console_container.pack(fill='both', expand=True, padx=30, pady=(0, 20))
tk.Frame(console_container, bg=THEME['border'], height=1).pack(fill='x', pady=0)
c_header = tk.Frame(console_container, bg=THEME['bg_primary']); c_header.pack(fill='x', pady=(10, 5))
tk.Label(c_header, text=f"{ICONS['terminal']} CONSOLE OUTPUT", font=FONTS['title'], fg=THEME['text_secondary'], bg=THEME['bg_primary']).pack(side='left')
btn_expand = tk.Button(c_header, text=ICONS['expand'], command=toggle_console, bg=THEME['bg_primary'], fg=THEME['accent_blue'], bd=0, font=('Segoe UI', 12), cursor='hand2', activebackground=THEME['bg_primary'], activeforeground='white'); btn_expand.place(relx=0.5, rely=0.5, anchor='center')
clear_box = tk.Frame(c_header, bg=THEME['bg_card'], highlightbackground=THEME['border'], highlightthickness=1, cursor='hand2'); clear_box.pack(side='right')
c_inner = tk.Frame(clear_box, bg=THEME['bg_card'], cursor='hand2'); c_inner.pack(padx=15, pady=8)
l_icon = tk.Label(c_inner, text=ICONS['trash'], font=('Segoe UI', 10), fg=THEME['text_primary'], bg=THEME['bg_card'], cursor='hand2'); l_icon.pack(side='left', padx=(0, 8))
l_text = tk.Label(c_inner, text="Clear", font=FONTS['body_bold'], fg=THEME['text_primary'], bg=THEME['bg_card'], cursor='hand2'); l_text.pack(side='left')
def on_clear_click(e): clear_console()
def on_enter_clear(e): clear_box.config(bg=THEME['border']); c_inner.config(bg=THEME['border']); l_icon.config(bg=THEME['border'], fg='white'); l_text.config(bg=THEME['border'], fg='white')
def on_leave_clear(e): clear_box.config(bg=THEME['bg_card']); c_inner.config(bg=THEME['bg_card']); l_icon.config(bg=THEME['bg_card'], fg=THEME['text_primary']); l_text.config(bg=THEME['bg_card'], fg=THEME['text_primary'])
for w in [clear_box, c_inner, l_icon, l_text]: w.bind('<Button-1>', on_clear_click); w.bind('<Enter>', on_enter_clear); w.bind('<Leave>', on_leave_clear)
log_box = scrolledtext.ScrolledText(console_container, bg=THEME['bg_console'], fg=THEME['text_console'], font=FONTS['console'], bd=0, height=10); log_box.pack(fill='both', expand=True, pady=(0, 0))
log_box.tag_configure('timestamp', foreground=THEME['accent_blue']); log_box.tag_configure('status', foreground='#22c55e'); log_box.tag_configure('error', foreground=THEME['status_error']); log_box.config(state='disabled')

# --- INIT ---
update_heartbeat_and_stats(); refresh_recovery_view()
log_raw(""); log_status(f"PRIME Service Portal Toolkit v6.30 initialized")
if not HAS_PSUTIL: log_message("Note: 'psutil' not found. Telemetry running in simulation mode.", tag='error')
if not HAS_PSYCOPG2: log_message("Note: 'psycopg2' not found. Database stats running in simulation mode.", tag='error')
if not HAS_PIL: log_message("Note: 'Pillow' (PIL) not found. Images disabled.", tag='error')
if not HAS_CALENDAR: log_message("Note: 'tkcalendar' not found. Recovery calendar disabled.", tag='error')
root.mainloop()