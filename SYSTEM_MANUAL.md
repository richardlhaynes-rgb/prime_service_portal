# PRIME Service Portal: Master Operations & Recovery Manual

**Version:** 2.4.2  
**Last Updated:** December 26, 2025  
**System Owner:** Richard Haynes  

---

## 1. Executive Summary

The PRIME Service Portal is a mission-critical internal IT Service Management (ITSM) platform. It provides centralized ticket management, a technical Knowledge Base, and Hardware Asset Tracking for the enterprise. The system is engineered for reliability, security, and scalability across 22 offices and 600+ employees.

---

## 2. Technical Architecture

This system is built using a professional, production-grade stack:

- **Language:** Python 3.14.0
- **Web Framework:** Django 5.2.8
- **Production Web Server:** **Waitress** (32-thread configuration for enterprise-wide stability)
- **Database Engine:** **PostgreSQL 18.1**
- **Frontend Technologies:** Tailwind CSS (Styling), HTMX (Dynamic updates), Django Templates

---

## 3. Critical File Locations

If you have the project folder, these are the only files that matter for survival:

- **`config/settings.py`**: Contains the "Secret Key" and the Database connection credentials.
- **`media/`**: **CRITICAL.** This folder contains every screenshot, user avatar, and attachment ever uploaded. It is NOT stored in the database.
- **`run_production.py`**: The entry point for the Waitress production server.
- **`requirements.txt`**: The list of all Python libraries required to build the system environment.
- **`control_center.pyw` / `Control_Center.bat`**: The PRIME Cockpit dashboard for managing the site and backups.
- **`static/images/logo_white.png`**: Official PRIME AE branding for all UI and admin tools.

---

## 4. Daily Operations (Start/Stop)

- **To Start the Portal:** Double-click `Start_Portal.bat`. This launches Waitress on `0.0.0.0:8000`, making it accessible to the entire network.
- **To Stop the Portal:** Close the command prompt window or press `Ctrl+C`.
- **Network Access:** Users can access the portal via `http://[Your-IP-or-Hostname]:8000`.

---

## 5. Data Protection (Backups)

The system requires a **Two-Part Backup** strategy:

1. **File Backup:** Copy the `media/` folder to a secure network drive weekly.
2. **Database Backup:** Run `Backup_Database.bat`. This uses `pg_dump` to create `portal_db_backup.sql`.  
   *Note: Ensure PostgreSQL 18.1 binaries are in your System Path.*

---

## 6. Disaster Recovery (Rebuilding the Site)

If the host computer is destroyed, follow these steps on a new machine:

1. **Install Prerequisites:** Install Python 3.14 and PostgreSQL 18.1.
2. **Restore Files:** Copy the project folder to the new machine.
3. **Environment Setup:**
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```
4. **Database Restore:**  
   - Create a blank database in Postgres named `prime_service_portal`.
   - Import your backup: `psql -U postgres prime_service_portal < portal_db_backup.sql`.
5. **Verify Settings:** Ensure `config/settings.py` reflects the new database password.
6. **Launch:** Run `Start_Portal.bat`.

---

## 7. Maintenance & Troubleshooting

- **Logs:** System events are logged to `system_logs.json` and are viewable via the "Workspace" tab in the portal.
- **Developer Mode:** If you need to debug code, use `python manage.py runserver` in your terminal to see detailed error screens. **Never** use this for the 600-person production environment.

---

## 8. Database Management: PostgreSQL vs. pgAdmin

**PostgreSQL Service (The Engine):**
- This is the actual database server running as a Windows Service (usually called `postgresql-x64-18`).
- It must be running for the PRIME Service Portal to function.
- All data (tickets, users, assets) is stored in the PostgreSQL engine.

**pgAdmin (The Dashboard):**
- pgAdmin is a graphical management tool for PostgreSQL.
- Use it to view, query, or manually edit database tables.
- Stopping pgAdmin does **not** stop the database service. The site will keep running as long as the PostgreSQL service is active.

**Summary:**  
- **PostgreSQL Service:** Must always be running for the portal to work.  
- **pgAdmin:** Optional, for database administration only.

---

## 9. PRIME Cockpit (`control_center.pyw`)

The PRIME Cockpit is the all-in-one administration dashboard for the Service Portal.

**Key Features:**

- **Professional UI:** Modern, high-contrast interface with a high-visibility branded sidebar using official PRIME AE colors and logo.
- **Centralized Operations:** Start/stop the production server, run migrations, refresh static assets, and trigger full system backups from a single window.
- **One-Click Cloud Snapshots:** Instantly back up the entire project and database to Google Drive (G:\).
- **Activity Log:** Real-time system log viewer for all admin actions.
- **Minimized Launcher:** `Control_Center.bat` launches the Cockpit in silent mode for a clean desktop workspace.

**How to Use:**

- Double-click `Control_Center.bat` to launch the Cockpit.
- Use the sidebar to access all major operations.
- The footer displays system version, database engine, and Django version in bold white text for instant visibility.

---

## 10. Network & Port Recovery

The Cockpit now includes advanced network and port management:

- **Port 8000 Monitoring:** The Cockpit surgically monitors Port 8000, which is used by both the development and production servers.
- **Safe Exit Protocol:** When exiting the Cockpit, the `safe_exit` protocol automatically scans for any process still listening on Port 8000.
- **PID Termination:** If the site remains accessible after closing the app, the Cockpit will locate and kill the specific PID associated with Port 8000, ensuring the browser connection is fully cleared and preventing "ghost" sessions.
- **Broad-Spectrum Kill:** Both `python.exe` and `pythonw.exe` are targeted to guarantee all server processes are stopped.

---

## 11. Hot Backup Logic (Full System Snapshot to G: Drive)

The Cockpit's "Full Cloud Snapshot" button performs a comprehensive backup:

1. **Database Dump:**  
   - Runs `pg_dump` to export the entire `prime_service_portal` database to a SQL file.
   - The SQL dump is saved in a dated folder on the `G:\My Drive\development\portal_backups` drive.

2. **Project Folder Copy:**  
   - Copies the entire project directory (including code, media, and virtual environment) to the same backup location.

3. **Result:**  
   - You get a complete, restorable snapshot: both the database and all files, ready for disaster recovery.

**To Restore:**  
- Use the SQL file to restore the database (see Section 6).
- Copy the project files back to a new machine as needed.

---

**For questions or emergencies, contact Richard Haynes (Service Desk Manager).**