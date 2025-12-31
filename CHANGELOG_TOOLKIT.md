# Changelog

All notable changes to the Service Portal Toolkit are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0/).

---

## [6.28.0] - 2025-12-31 (Git Integration Edition)

### 🚀 New Features
- **Smart Git Push:** Integrated a seamless "Git Push" workflow into the Dev Tools tab.
  - Automatically stages (`git add .`) all changes.
  - Prompts for a custom commit message via popup.
  - Executes push and streams the console output back to the Toolkit UI for real-time feedback.

---

## [5.4.3] - 2025-12-28 (Self-Documenting Edition)

### 🚀 New Features
- **Integrated Changelog Access:** The application version number in the header is now a clickable link that launches this changelog file.

### ⚙️ Backend & Architecture
- **Full Readability Refactor:** Expanded the codebase back to "Long-Hand" format with comprehensive comments for maximum maintainability.

---

## [5.4.2] - 2025-12-28 (Refined Polish)

### 🎨 UI & UX Polish
- Simplified Snapshot List headers to remove redundant "Time" labels.
- Standardized column headers to "Eastern Time (US & Canada)".

---

## [5.4.0] - 2025-12-28 (Explorer Edition)

### 🚀 New Features
- **In-App File Browser:** Added a native, dark-themed file explorer to the Recovery Dashboard.
- **Navigation Logic:** Implemented "Up Level" navigation and double-click folder traversal within the backup root.

### 🎨 UI & UX Polish
- Implemented a 3-State Dashboard View: seamless toggling between Snapshot List, Restore Guide, and File Browser.

---

## [5.3.0] - 2025-12-28 (Humanization Update)

### 🎨 UI & UX Polish
- **Smart Date Formatting:** Converted raw database timestamps to human-readable relative dates ("Today", "Yesterday", "Thursday, Dec 25").
- **12-Hour Time:** Converted 24-hour logs to 12-hour format (e.g., 9:12 PM).
- Adjusted column widths in the Snapshot Treeview for better readability.

---

## [5.2.0] - 2025-12-28 (Focus Mode)

### 🎨 UI & UX Polish
- **Restore Focus View:** Clicking "RESTORE" now hides the calendar and expands the instructions to full-width for better legibility.
- Added smart toggling to restore the split-view layout when returning to the snapshot list.

---

## [5.1.0] - 2025-12-28 (Guidance System)

### 🚀 New Features
- **Restore Wizard (UI):** Embedded a detailed, read-only text guide within the app detailing the manual restore process.
- **Active Calendar Filtering:** Clicking a date on the calendar now instantly filters the snapshot list to show only backups from that specific day.

### ⚙️ Backend & Architecture
- Deprecated the generation of external `HOW_TO_RESTORE.txt` files in favor of the in-app guide.

---

## [5.0.0] - 2025-12-28 (Plug-n-Play Architecture)

### ⚙️ Backend & Architecture
- **Auto-Dependencies:** The backup engine now runs `pip freeze > requirements.txt` automatically before every snapshot.
- **Config Capture:** The system now locates and backs up the local `pgpass.conf` file to a `_config` folder for seamless database authentication restoration.
- **Portable Snapshots:** Finalized logic to ensure backups are machine-agnostic (excluding environment-specific paths).

---

## [4.9.2] - 2025-12-28 (Silent Runner)

### 🎨 UI & UX Polish
- **Inline Feedback:** Removed intrusive "Backup Complete" popup dialogs.
- Added a self-clearing "✔ Snapshot Complete" status message directly in the toolbar.

---

## [4.9.0] - 2025-12-28 (Smart Engine)

### ⚙️ Backend & Architecture
- **Smart Walker Engine:** Replaced simple directory copying with a threaded file walker.
- **Intelligent Exclusions:** Added logic to strictly ignore `venv`, `.git`, and `__pycache__`, reducing backup size by ~90% and increasing speed.
- **Progress Tracking:** Implemented a real-time progress bar that tracks file copy operations and database dumping phases.

---

## [4.8.0] - 2025-12-28 (Dashboard Redesign)

### 🚀 New Features
- **Recovery Dashboard:** Replaced the simple button menu with a split-pane layout featuring a permanent Calendar and Snapshot List.
- **Console Drawer:** Implemented a collapsible "Terminal" drawer that slides up over the dashboard for debugging.

### 🎨 UI & UX Polish
- Added "Work Area Awareness" to center the application optically, respecting the Windows Taskbar.

---

## [4.7.0] - 2025-12-28 (The Modern Overhaul)

### 🚀 New Features
- **Complete UI Rewrite:** Transitioned to a "Slate & Blue" DevOps aesthetic.
- **Live Telemetry:** Added real-time CPU and RAM usage graphs using `psutil`.
- **Process Management:** Integrated "Start/Stop" controls for Production (Waitress) and Development (Django) servers with PID tracking.
- **Network Intelligence:** Added logic to detect the active IPv4 Gateway, filtering out IPv6 noise.

---

## [2.7.18] - 2025-12-26 (Stabilized Navigator Edition)

### 🚀 New Features
- Verified double-click bindings for the Calendar Explorer to launch Windows File Explorer directly.

### ⚙️ Backend & Architecture
- Implemented directory guards to prevent application locking/freezing on empty states or missing backup directories.

### 🎨 UI & UX Polish
- Added dynamic centering for archives: standardized to 1-column for ≤ 5 items and 2-columns for 6-10 items.

---

## [2.7.17] - 2025-12-26 (Nested Versioning Edition)

### ⚙️ Backend & Architecture
- Overhauled backup architecture to a hierarchical 'Date -> Time -> Project/DB' structure for enterprise-grade drive organization.

---

## [2.7.14] – [2.7.16] - 2025-12-26 (Calibration Sprint)

### ⚙️ Backend & Architecture
- Resolved regex date parsing conflicts for folders containing unique timestamps.
- Integrated list-based mapping to support multiple snapshots per single calendar day without data collision.

---

## [2.7.8] – [2.7.13] - 2025-12-26 (Visual Perfection)

### 🚀 New Features
- Launched the Snapshot Navigator calendar popup for high-fidelity history browsing.

### 🎨 UI & UX Polish
- Developed the 'Hybrid Navigator' layout featuring a top-10 display grid and history link.
- Surgically removed blue underlines and horizontal separators to achieve a clean-text aesthetic.

---

## [2.7.7] - 2025-12-26 (Symmetry Calibration)

### 🎨 UI & UX Polish
- Established 'Leading Newline Logic' to standardize vertical rhythm and padding in the activity log.

---

## [2.7.6] - 2025-12-26

### 🚀 New Features
- Initial baseline release of the Service Portal Toolkit.