# PRIME Service Portal: Master Operations & Recovery Manual

**Version:** 1.0  
**Last Updated:** December 25, 2025  
**System Owner:** Richard Haynes  

---

## 1. Executive Summary
The PRIME Service Portal is a mission-critical internal IT Service Management (ITSM) platform. It provides centralized ticket management, a technical Knowledge Base, and Hardware Asset Tracking for the enterprise. It is designed to scale across 22 offices and 600+ employees.

## 2. Technical Architecture
This system is built using a professional "Production-Grade" stack to ensure stability and data integrity.

* **Language:** Python 3.14.0
* **Web Framework:** Django 5.2.8
* **Production Web Server:** **Waitress** (Configured for 32 threads to handle enterprise-wide traffic)
* **Database Engine:** **PostgreSQL 18.1**
* **Frontend Technologies:** Tailwind CSS (Styling), HTMX (Dynamic updates), and Django Templates

---

## 3. Critical File Locations
If you have the project folder, these are the only files that matter for survival:
* **`config/settings.py`**: Contains the "Secret Key" and the Database connection credentials.
* **`media/`**: **CRITICAL.** This folder contains every screenshot, user avatar, and attachment ever uploaded. It is NOT stored in the database.
* **`run_production.py`**: The entry point for the Waitress production server.
* **`requirements.txt`**: The list of all Python libraries required to build the system environment.
* **`control_center.py` / `Control_Center.bat`**: The Control Center dashboard for managing the site and backups.

---

## 4. Daily Operations (Start/Stop)
The system should **not** be run via VS Code in a production environment. 

* **To Start the Portal:** Double-click `Start_Portal.bat`. This launches Waitress on `0.0.0.0:8000`, making it accessible to the entire network.
* **To Stop the Portal:** Close the command prompt window or press `Ctrl+C`.
* **Network Access:** Users can access the portal via `http://[Your-IP-or-Hostname]:8000`.

---

## 5. Data Protection (Backups)
The system requires a **Two-Part Backup** strategy:
1.  **File Backup:** Copy the `media/` folder to a secure network drive weekly.
2.  **Database Backup:** Run `Backup_Database.bat`. This uses `pg_dump` to create `portal_db_backup.sql`. 
    * **Note:** Ensure PostgreSQL 18.1 binaries are in your System Path.

---

## 6. Disaster Recovery (Rebuilding the Site)
If the host computer is destroyed, follow these steps on a new machine:

1.  **Install Prerequisites:** Install Python 3.14 and PostgreSQL 18.1.
2.  **Restore Files:** Copy the project folder to the new machine.
3.  **Environment Setup:**
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```
4.  **Database Restore:** * Create a blank database in Postgres named `prime_service_portal`.
    * Import your backup: `psql -U postgres prime_service_portal < portal_db_backup.sql`.
5.  **Verify Settings:** Ensure `config/settings.py` reflects the new database password.
6.  **Launch:** Run `Start_Portal.bat`.

---

## 7. Maintenance & Troubleshooting
* **Logs:** System events are logged to `system_logs.json` and are viewable via the "Workspace" tab in the portal.
* **Developer Mode:** If you need to debug code, use `python manage.py runserver` in your terminal to see detailed error screens. **Never** use this for the 600-person production environment.

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

## 9. Control Center Dashboard (`control_center.py` / `Control_Center.bat`)

The Control Center provides a single dashboard to manage all critical operations for the PRIME Service Portal.

**Launching the Control Center:**
- Double-click `Control_Center.bat` in the project root.
- This opens a graphical dashboard with buttons for all major operations.

**Key Features:**
- **Start Production Site:** Launches the Waitress server for enterprise-wide access.
- **Refresh System Assets:** Runs `collectstatic` to sync static files for production.
- **Refresh Tickets:** Runs the ticket data sync process.
- **Full Cloud Snapshot:** Runs a "Hot Backup" (see below).
- **Start Dev Server:** Launches Django's development server for safe testing.

---

## 10. Hot Backup Logic (Full System Snapshot to G: Drive)

The Control Center's "Full Cloud Snapshot" button performs a comprehensive backup:

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