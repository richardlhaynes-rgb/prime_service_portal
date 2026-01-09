# Changelog

All notable changes to the PRIME Service Portal project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0/).

---

## [2.9.0] - 2026-01-08 (Collaborative Support & UI Refinement)

### 🚀 New Features
- **Collaborator System:** Added the ability to assign multiple "Collaborators" to a ticket alongside the primary Technician, enabling team swarming on complex issues.
- **Smart Chip Interface:** Implemented a multi-select "Chip" UI for managing Assignees and Collaborators on both the New Ticket (Agent) form and Ticket Detail sidebar.
- **Team Visibility:** Updated the **Workspace** "Res" column and **User Dashboard** "Support" column to display "+N" badges, revealing the full team working on a ticket via tooltip.
- **Watcher Indicators:** Technicians now see a specific "Eye" icon in their grid view for tickets where they are a Collaborator but not the Primary Owner.

### ⚙️ Backend & Architecture
- **Schema Expansion:** Updated `Ticket` model to include a `collaborators` ManyToMany relationship with `User`.
- **Search Logic Refactor:** Standardized user search results into `full` (Rich) and `compact` (Avatar/Name only) variants to support high-density UI zones.
- **Query Optimization:** Added `prefetch_related` lookups to Dashboard and Workspace views to efficiently load collaborator data without N+1 query performance hits.
- **Scope Restriction:** Restricted Assignee and Collaborator search results to strictly filter for members of the 'Service Desk' group.

### 🎨 UI & UX Polish
- **Context-Aware Density:** Applied the new `compact` search variant to the Ticket Detail sidebar and Agent Create form to eliminate horizontal scrollbars and visual clutter.
- **Dashboard Transparency:** Added a "Support" column to the End-User Dashboard, giving users full visibility into who is handling their request.
- **Agent Ergonomics:** Added an "Assign to Me" shortcut link to the Agent Create Ticket form for rapid self-assignment.

---

## [2.8.0] - 2026-01-06 (Omni-Search & Registry Architecture)

### 🚀 New Features
- **Omni-Search Engine:** Implemented a global, real-time search bar (HTMX) that simultaneously queries Tickets, Hardware Assets, Users, and Knowledge Base articles.
- **Ticket Registry:** Launched a dedicated "Power Search" interface allowing deep filtering by Status, Priority, Technician, Submitter, and Service Board with persistent URL parameters.
- **User Dossier:** Introduced a safe "Read-Only" profile view for general search results, displaying contact info, assigned assets, and recent ticket history (replacing the risky "Edit User" form link).
- **Asset History Bridge:** Asset Detail views now dynamically aggregate and display all tickets referencing the specific Asset Tag, creating a complete hardware lifecycle history.

### ⚙️ Backend & Architecture
- **Search Logic Expansion:** Updated query logic to include Technician and Submitter identities (First Name, Last Name, Username) in global keyword searches.
- **Navigation Bridging:** Created a "Bridge" link in the Omni-Search footer that passes the current search query directly to the Ticket Registry for advanced filtering.
- **Routing Standardization:** Formalized `asset_detail` and `user_dossier` URL patterns to ensure consistent linking across the application.

### 🎨 UI & UX Polish
- **Search Ergonomics:** Replaced the non-functional "ESC" visual badge in the search modal with a fully interactive "Close" icon.
- **Visual State Management:** Fixed a JavaScript regression in System Logs where date filter buttons (Today, 7d) failed to highlight when active.
- **Workspace Integration:** Added a "Ticket Registry" shortcut button to the Technician Workspace toolbar for quick access to historical data.

---

## [2.7.0] - 2026-01-04 (Asset Intelligence & Data Integrity)

### 🚀 New Features
- **Advanced Spec Tracking:** Expanded the Asset Schema to capture "Memory Type" (DDR5, Unified, ECC) and detailed Display Specifications (Resolution, Refresh Rate, Panel Type).
- **Split-Storage Workflow:** Redesigned the Storage input logic to support separate "Primary" (OS) and "Secondary" (Data) drives with distinct Size/Technology controls.
- **Dynamic Dashboard Filters:** Replaced static headers with a live-query "Category" dropdown that automatically adapts to the database taxonomy.
- **Enterprise Taxonomy:** Expanded the system to support 5 new asset classes: Servers, Printers & Plotters, AV & VR Equipment, Peripherals, and Network Infrastructure.

### ⚙️ Backend & Architecture
- **Seeding Engine V2:** Completely rewrote `seed_assets.py` with context-aware logic (e.g., assigning Static IPs to Printers, RAID arrays to Servers, and Dual Monitors to users).
- **Query Optimization:** Updated `views.py` to actively process Category filters and changed the default dashboard sorting to **Asset Tag (Ascending)**.
- **URL Encoding Safety:** Implemented `|urlencode` filters in templates to prevent cutoff errors when filtering categories with special characters (e.g., "AV & VR").

### 🎨 UI & UX Polish
- **Form Ergonomics:** Rebuilt the "System Configuration" form into a 4x2 aligned grid with custom-styled "HDD/SSD" toggle switches.
- **Visual Detail Views:** Overhauled the Asset Detail page to render new spec fields (Port Badges, Curved Display tags) and split storage rows.
- **Interface Stability:** Resolved CSS clipping issues on the Dashboard card to ensure dropdown menus float correctly over table boundaries.
- **Scroll Management:** Added `max-height` and internal scrolling to the Category Dropdown to support extensive lists without breaking the page layout.

---

## [2.6.0] - 2026-01-03 (Asset Inventory Expansion)

### 🚀 New Features
- **Mobile Asset Workflow:** Introduced dedicated categories and logic for **Smartphones**, **Tablets**, and **Mobile Hotspots**.
- **Cellular Tracking:** Added a "Mobile Broadband" configuration card capturing IMEI, ICCID, Carrier, Data Plan, and Contract details.
- **Smart Forms:** Implemented category-driven UI logic that automatically hides irrelevant sections (e.g., hiding "Network Connectivity" for phones, hiding "CPU/GPU" specs for Hotspots).
- **Dynamic Placeholders:** Input fields now adapt their example text based on the selected category (e.g., showing "iOS 17" for OS when "Smartphone" is selected).

### ⚙️ Backend & Architecture
- **Data Hygiene Engine:** Added a pre-submission JavaScript layer that wipes data from hidden fields to prevent database pollution when changing asset categories.
- **Routing Stability:** Patched a critical `404` error on the "Add Asset" screen by restructuring Django URL pattern ordering (Specific > Wildcard).
- **Schema Evolution:** Expanded the JSON-based `specs` storage to handle mobile-specific data points (`mob_carrier`, `mob_imei`, etc.) alongside traditional computing specs.

### 🎨 UI & UX Polish
- **Contextual Views:** Refined the Asset Detail page to strictly "Hide if Empty," ensuring clean layouts for assets with missing specs.
- **Lifecycle Alerts:** Added distinct "EXPIRED" badges for Mobile Contract End Dates to differentiate them from Hardware Warranty status.
- **Visual Streamlining:** Removed "Desktop-grade" fields (Processor, Graphics, RAM) from the Smartphone view to focus on relevant stats (OS, Storage).

---

## [2.5.0] - 2025-12-31 (Notifications & Reporting Stability)

### 🚀 New Features
- **Notification Workflow:** Replaced the destructive "Clear All" action with a safer "Mark All as Read" button in the dropdown.
- **Persistent Navigation:** Added a permanent "View All History" footer link to the Notification dropdown, ensuring accessibility even when the queue is empty.
- **CSAT Visuals:** Added user avatars to the Customer Satisfaction Report feedback list for a more personalized view.

### ⚙️ Backend & Architecture
- **Legacy URL Routing:** Implemented intelligent URL parsing in `views.py` to automatically correct legacy or seed-data paths (e.g., routing `/ticket/123/` to the correct `/service-desk/ticket/123/`).
- **Data Simulation:** Updated the ticket seeding script (`seed_tickets.py`) to bypass `auto_now_add` restrictions, allowing for the generation of realistic historical data for analytics testing.
- **CSRF Hardening:** Secured HTMX actions in the notification dropdown by explicitly injecting CSRF tokens into headers.

### 🎨 UI & UX Polish
- **Notification Hover:** Fixed a CSS regression where hovering over a single notification would highlight all items in the list (implemented Tailwind "Named Groups").
- **CSAT Context:** Added a "Filtering by Technician" banner to the CSAT report to provide better context when viewing individual performance stats.

### 🐛 Fixes
- **CSAT Crashes:** Resolved a `NoReverseMatch` error on the CSAT report by passing raw ticket IDs to the template URL generator.
- **Scope Leak:** Fixed an issue where the "Global" header would persist even when viewing a specific technician's report.
- **Data Filters:** Corrected date filtering logic in reports to properly include data from the current day.

---

## [2.4.2] - 2025-12-26 (Process Management)

### 🚀 New Features
- **Port Hygiene:** Integrated a "Port-Surgical" exit protocol using netstat to definitively kill processes on Port 8000 to prevent browser ghosting.

### ⚙️ Backend & Architecture
- **Process Cleanup:** Implemented broad-spectrum taskkill for both `python.exe` and `pythonw.exe` within the safe_exit protocol.

### 🎨 UI & UX Polish
- **Footer Visibility:** Updated sidebar technical footer to White 9pt Bold for high visibility.
- **Window Geometry:** Refined window height to 850px for perfect desktop centering.

---

## [1.3.0] - 2025-12-25 (Control Center & Backup)

### 🚀 New Features
- **PRIME Control Center:** Launched a custom GUI administration dashboard (`control_center.py`) for centralized site management.
- **Automated Cloud Snapshots:** Integrated a "One-Click" backup system that clones the entire project and database to Google Drive (G:\).
- **Minimized Launcher:** Created a silent .bat launcher for the Control Center to maintain a clean desktop workspace.
- **Silent Execution:** Transitioned the Cockpit to `.pyw` for silent background execution.

### ⚙️ Backend & Architecture
- **Infrastructure Finalization:** Completed the transition to PostgreSQL 18.1 as the primary production engine.
- **Static Asset Pipeline:** Implemented `collectstatic` workflows and absolute path mapping to ensure 100% image reliability across Network IPs and Hostnames.
- **Security Hardening:** Configured `ALLOWED_HOSTS` to support multi-office network access via specific IP and Hostname identities.

### 🎨 UI & UX Polish
- **Production Console:** Enhanced the Waitress startup screen with professional ANSI coloring and dynamic network access discovery.
- **Custom Branding:** Created and deployed a high-fidelity SVG/ICO icon for the system's administration tools.
- **Visual Branding:** Implemented the professional "Manager Analytics" slate palette and replaced rocket icons with the official white PRIME AE logo mapping.

---

## [1.2.0] - 2025-12-25 (Production Deployment)

### 🚀 New Features
- **Production Server:** Implemented `Waitress` WSGI server with a 32-thread configuration for enterprise-wide stability.
- **One-Click Launchers:** Created `Start_Portal.bat` and `run_production.py` for professional deployment without VS Code.
- **Disaster Recovery:** Created `SYSTEM_MANUAL.md` and `Backup_Database.bat` for "Bus Factor" business continuity.
- **Asset Management Foundation:** Added initial `Asset` model to `models.py` with lifecycle status tracking.
- **UI Enhancements:** Added Submitter name, precision timestamps, and Dark-Mode-aware attachment displays to Ticket Details.

### ⚙️ Backend & Architecture
- **Database Migration:** Successfully migrated core engine from SQLite to PostgreSQL 18.1.
- **Log System:** Refactored `log_system_event` to resolve database locking issues during concurrent writes.
- **File Handling:** Updated ticket submission views to correctly handle and store `request.FILES` attachments.

### 🐛 Fixes
- **Template Safety:** Resolved "VariableDoesNotExist" error on unassigned tickets by adding safe technician checks in templates.
- **Content Rendering:** Fixed HTML rendering in ticket descriptions using the `|safe` filter.
- **Attachment Display:** Optimized attachment display to show clean filenames instead of full system paths.

---

## [0.13.0] - 2025-12-24 (Profile Architecture & Stability)

### 🚀 New Features
- **Unified Profile System:** Consolidated the *Edit User* (Admin) and *My Profile* (Self) views into a single, maintainable template (`user_profile.html`).
- **Profile Stability:** Refactored the "Update User" logic to robustly handle avatar uploads and data persistence across all user roles.

### 🎨 UI & UX Polish
- **Avatar Cropping:** Applied smart positioning (`object-top`) to user avatars to prevent faces from being cut off in circular frames.
- **Login Status:** Fixed the "Last Login" display to show "Never" instead of broken timestamp strings for new accounts.
- **Error Feedback:** Enabled proper error reporting on profile forms to prevent silent failures during updates.

### ⚙️ Backend & Architecture
- **Root Import Fixes:** Corrected Python import paths for `services.ticket_service`, resolving `ModuleNotFoundError` crashes.
- **Manual File Handling:** Updated `views.py` to manually process `request.FILES` for avatar uploads, bypassing form restriction issues.
- **Validation Logic:** Switched read-only fields from `disabled` (not sent) to `readonly` (sent) to ensure forms pass server-side validation.

### 🐛 Fixes
- **Technician Analytics:** Resolved a `TemplateSyntaxError` in the Manager Dashboard caused by an invalid `startswith` filter.
- **Crash Prevention:** Fixed a critical `NameError` by importing `UserProfile` and logging services correctly in `views.py`.

---

## [0.12.0] - 2025-12-24 (Technician Workspace & System Hardening)

### 🚀 New Features
- **Technician Workspace:** Launched a fully interactive Kanban board for staff (`/service-desk/workspace/`). Features drag-and-drop status updates and a dedicated navigation link.
- **Data Source Selector:** Replaced the legacy "Maintenance Mode" toggle in Site Configuration with a clear "Data Source" selector (Internal DB vs. ConnectWise PSA).
- **Notification Management:** Added bulk deletion capabilities to the Notification History page, allowing users to scrub old alerts.
- **Role-Based Visualization:** Kanban cards now distinctively separate the Submitter (User Icon) from the Assigned Technician (Wrench Icon/Badge).

### 🎨 UI & UX Polish
- **Dark Mode Typography:** Fixed invisible or low-contrast text headers across the Service Catalog, System Health Settings, and System Logs pages.
- **Navigation Standardization:** Aligned spacing, colors, and icons in the main navigation bar (restored Book icon for Knowledge Base, Toolbox for Workspace).
- **Kanban Aesthetics:** Fixed the "To Do" column header background color in Dark Mode to match the rest of the board.
- **Visual Hierarchy:** Added a clean divider line and role-specific iconography to Kanban cards to reduce visual clutter.

### ⚙️ Backend & Architecture
- **Resilient Deletion Logic:** Updated `delete_notifications` view to handle multiple checkbox payload names (`notification_ids`, `pk`, `selection`) to ensure template compatibility.
- **Honest Form Binding:** Refactored Site Configuration to bind radio buttons directly to `use_mock_data`, removing "ghost inputs" and hidden fields.
- **Routing Optimization:** Renamed Kanban routes to `/workspace/` to match the frontend terminology.

### 🐛 Fixes
- **Routing Error:** Resolved 404 errors on the Kanban board by correcting internal URL patterns in the Service Desk app.
- **Selection Failure:** Fixed the "No notifications selected" error during bulk delete operations by broadening the backend parameter search.
- **Button Sizing:** Standardized the "Delete" button size in the Notification toolbar to match existing "Mark Read/Unread" buttons.

---

## [0.11.0] - 2025-12-23 (Dashboard Interactivity & System Control)

### 🚀 New Features
- **Interactive Dashboard:** Metric cards (Open, Resolved, History) are now clickable filters that instantly toggle the ticket table view.
- **Smart Pagination:** Implemented client-side pagination for Dashboard (10 rows) and System Logs (15 rows) with auto-hiding controls.
- **System Logs "Control Deck":** Overhauled the header into a pro-grade command center with Date Range presets (Today, Yesterday, 7d, 30d) and Custom Date support.
- **HTMX Ready:** Injected the HTMX library into the base template to support future high-performance partial reloads.

### 🎨 UI & UX Polish
- **Dashboard Focus:** Default view now auto-filters to "Open Tickets" on load to prioritize action items.
- **Visual Consistency:** System Logs date controls now match the "Manager Analytics" styling 1:1 (Dark Mode optimized, specific button borders/colors).
- **Icon Harmony:** Standardized the Management Hub gear icon's hover state to White (matching the Theme toggle) and restored the correct outline SVG.

### ⚙️ Backend & Architecture
- **Log Filtering Engine:** Rewrote `system_logs` view logic to process semantic date ranges (`today`, `yesterday`) and custom datetime windows.
- **Security Hardening:** Restricted visibility of the Management Hub (Settings) navigation link to Superusers only.

### 🐛 Fixes
- **Broken Links:** Fixed the Management Hub icon link pointing to a non-existent URL name.
- **Hover States:** Corrected disjointed hover states in the main navigation header.

---

## [0.10.0] - 2025-12-21 (User Identity & Data Integrity)

### 🚀 New Features
- **Enhanced User Profiles:** Expanded the data model to include Company, Manager, and Office Location fields.
- **Identity Privacy Controls:** Introduced a "Prefer Initials" toggle, allowing users to override their profile photo with a generated avatar.
- **Smart Avatar Engine:** Implemented instant JavaScript previews that update immediately when uploading a file or toggling the "Initials" setting.
- **Expanded Ticket Schema:** Added missing ticket types (General Question, VP Password Reset, VP Permissions) to the database model.

### 🎨 UI & UX Polish
- **"Clean Split" Header Design:** Redesigned the *Edit User* screen with a balanced "Identity vs. Status" layout.
- **Visual Account Stats:** Added right-aligned badges (Active, Staff, Superuser) and "Member Since/Last Login" timestamps to the user header.
- **Instant Feedback:** Avatar previews now react in real-time to user inputs (uploads or checkbox toggles) before saving.
- **Consistent Badging:** Standardized user badges across the User Management list and Edit User screens.

### ⚙️ Backend & Architecture
- **Data Generator Overhaul:** Rewrote `generate_demo_tickets.py` to populate the new profile fields and assign realistic office locations.
- **Status Standardization:** Standardized the ticket workflow to use "Resolved" (removing references to the invalid "Closed" status).
- **Form Bridge:** Updated `CustomUserChangeForm` to explicitly handle persistence for `UserProfile` fields (Company, Manager, etc.).
- **URL Safety:** Hardcoded robust URL lookups in templates to prevent `NoReverseMatch` errors on navigation buttons.

### 🐛 Fixes
- **Generator Crash:** Fixed `AttributeError: type object 'Status' has no attribute 'CLOSED'` during demo data generation.
- **Missing Options:** Fixed "General Question" tickets failing to save due to missing database choices.
- **Avatar Consistency:** Fixed an issue where the "Prefer Initials" setting was randomly applied by the generator, causing UI inconsistencies.
- **Broken Links:** Repaired navigation buttons on the User Edit form by syncing URL names with `urls.py`.

---

## [0.9.0] - 2025-12-17 (Dark Mode Perfection)

### 🚀 New Features
- **Smart Save Logic:** "Save Changes" buttons on System Health and Settings pages now detect "dirty" forms (typing or template selection) and remain disabled until changes occur.
- **Public Status Links:** Converted "Service Status" dropdown items into direct links to public vendor health dashboards (Office 365, Autodesk, Egnyte, etc.).
- **Semantic Editor Toolbars:** Knowledge Base editor toolbars are now color-coded (Red for Issue, Green for Resolution, Yellow for Private Notes) to reinforce context.

### 🎨 UI & UX Polish
- **Dark Mode Completion:** Eliminated "white flash" artifacts across all search bars (System Logs, KB Manager, User List) using global autofill overrides.
- **System Log Styling:** Refined "Create" action icons to use transparent "glass" backgrounds (`bg-green-900/20`) instead of solid white stickers.
- **Report Readability:** "Dimmed" inactive date range buttons on CSAT and Manager Dashboards to reduce visual noise in Dark Mode.
- **Dropdown Optimization:** Widened the Global Status dropdown (w-96) to prevent text wrapping on long status messages (e.g., "Degraded Performance").
- **Table Stability:** Enforced fixed column widths on System Logs to prevent layout shifting when toggling Time Zones.

### 🐛 Fixes
- **Layout Regressions:** Fixed "System Logs" header and table stacking issues caused by flex container conflicts.
- **Icon Restoration:** Restored the classic "Pencil" icon for Edit actions in the KB Manager (replacing the generic list icon).
- **Date Picker Contrast:** Fixed unreadable white-on-white text in "Custom Range" date inputs during Dark Mode.
- **Autofill Flash:** Applied CSS overrides to neutralize browser-forced white backgrounds on auto-completed inputs.

---

## [0.8.0] - 2025-12-09 (Admin Power Tools)

### 🚀 New Features
- **User Management Suite:** Complete admin interface to Add, Edit, Search, and Delete users.
- **Taxonomy Manager:** Split-pane interface in Site Configuration to dynamically add/delete KB Categories and Subcategories.
- **Audit Trail:** Added "Created By," "Modified By," and "Accessed" history tracking to User Profiles using Django LogEntry.
- **Smart User Forms:** Auto-generating usernames, "Suggest Strong Password" generator, and Native Browser Validation bubbles.

### 🎨 UI & UX Polish
- **Phantom Actions:** Table action buttons (Edit/Delete) remain hidden until row hover to reduce visual clutter.
- **Iconography:** Replaced text pills with intuitive Heroicons for User Roles (Shield/Briefcase) and Status (Check/Ban).
- **Settings Layout:** Refactored Site Configuration into a Sidebar/Tabbed interface for better scalability.
- **Unified Avatar UI:** Standardized the "Hero Header" profile photo uploader across My Profile and Edit User screens.
- **Flush Alignment:** Corrected vertical rhythm and panel alignment on configuration pages.

### ⚙️ Backend & Architecture
- **Database Normalization:** Migrated KB Categories from hardcoded text strings to relational `KBCategory` models (Bridge Strategy).
- **Self-Healing Data:** Implemented logic to auto-create missing `UserProfile` rows for legacy accounts on save.
- **Security:** Added `autocomplete="new-password"` attributes to admin forms to prevent browser autofill.
- **Routing:** Restored missing authentication routes (`login`) to prevent redirect loops.

### 🐛 Fixes
- **Crash Prevention:** Fixed `RelatedObjectDoesNotExist` crash when uploading avatars for older user accounts.
- **Migration Conflict:** Resolved "Table already exists" conflicts during taxonomy migration.
- **Alignment:** Fixed layout alignment issues where setting panels were not flush with the sidebar.

---

## [0.7.0] - 2025-11-29 (System Logs & Final Polish)

### 🚀 New Features
- **System Activity Logs:** Added full audit trail stored in `data/system_logs.json` (actions: Login, Update, Delete).
- **Log Viewer:** New System Logs page with search, sorting, and Windows-style timestamps.
- **Time Zone Support:** Dynamic selector (ET, CT, MT, PT, AKT, HST) converting UTC log entries.
- **User Menu:** Detached “Windows 11 Style” flyout with name/title and secure POST Sign Out.

### 🎨 UI & UX Polish
- **Table Icon Columns:** Standardized center-center alignment across Dashboard and KB Manager.
- **KB Manager Toolbar:** Fixed vertical spacing and padding consistency.

### ⚙️ Backend & Architecture
- **Logging Pipeline:** Implemented `log_system_event()` in `services/ticket_service.py` enforcing max 500 retained entries.
- **System Health Integration:** Updated update flow to emit audit entries on changes.
- **Time Zone Handling:** Added conversion logic at view layer for log timestamps.

### 🐛 Fixes
- **CSAT Report:** Repaired technician-specific feedback loading.
- **KB Manager:** Restored search + filter chaining and corrected toolbar layout.

---

## [0.6.0] - 2025-11-28 (The Feature Complete Update)

### 🚀 New Features
- **Knowledge Base Editor:** Full CRUD for articles (Add, Edit, Delete, Manage).
- **Bulk Article Actions:** Multi-select with status transitions (Draft, Pending, Approved).
- **Management Hub:** Central admin launchpad (Analytics, Settings, Logs, KB Manager).
- **Scheduled Announcements:** Start/End datetime support for system banners.

### 🎨 UI & UX Polish
- **Consistent Visuals:** Consistent table sorting visuals and icon-only status badges.
- **KB Listing:** Category sidebar, improved hover states, refined spacing.
- **Navigation:** Streamlined admin access model; unified header alignment.

### ⚙️ Backend & Architecture
- **View Consolidation:** Merged KB editor views into `service_desk/views.py`.
- **Data Taxonomy:** Normalized KB categories and subcategories (ConnectWise alignment).
- **Icon Injection Pipeline:** Dynamic icon resolution via mappings in `services/ticket_service.py`.
- **System Health Enhancements:** Added scheduling fields to persisted structure.

### 🐛 Fixes
- **Submission Errors:** Fixed article editor submission errors (import path corrections).
- **Profile Routing:** Technician profile 404 (moved to slug-based routing).
- **Persistence:** Announcement scheduling persistence.
- **Icon Fallbacks:** KB icon fallback elimination (all mapped).

---

## [0.5.0] - 2025-11-27 (Architecture Sprint)

### 🚀 New Features
- **Global System Health Banner:** Slim status bar with vendor dropdown.
- **Admin CMS:** `/manager/settings/` for modifying announcements + vendor statuses.
- **Ticket Survey:** CSAT form workflow (star rating demo implementation).

### 🎨 UI & UX Polish
- **Modern Tables:** Dashboard tables modernized (hover rows, icon column alignment).
- **Visual Adjustments:** Manager analytics visual adjustments (stable chart heights).
- **Service Catalog:** Service Catalog grid final styling pass.

### ⚙️ Backend & Architecture
- **Context Processor:** Injected system health globally.
- **Technician Roster:** Migrated to URL-safe slug IDs (e.g., `richard_haynes`).
- **Demo Mode Pattern:** Centralized mock retrieval through service layer toggle (`USE_MOCK_DATA`).

### 🐛 Fixes
- **Chart Overflow:** Chart overflow growth bug.
- **UI Logic:** Dropdown close behavior and minor survey persistence issues.
- **Broken Links:** Broken profile links due to space-containing identifiers.

---

## [0.4.0] - 2025-11-26 (Manager Analytics)

### 🚀 New Features
- **Manager Dashboard:** Added Chart.js widgets (Volume by Status, Tickets by Type, Trend, Resolution Time).
- **Technician Profiles:** Individual performance views (open tickets, CSAT, recent activity).
- **Team Roster:** Grid layout with dynamic open ticket badges.

### 🎨 UI & UX Polish
- **Hero Banners:** Introduced hero banners for technician profiles.
- **Analytics Cards:** Refined analytics cards and consistent spacing for metric sections.

### ⚙️ Backend & Architecture
- **Data Model Expansion:** Expanded analytics data model in `services/ticket_service.py`.
- **Roster Generation:** Generated technician roster records with stats and feedback arrays.

### 🐛 Fixes
- **Sorting:** Minor sorting inconsistencies on manager views.
- **Navigation:** Profile navigation reliability across roster IDs.

---

## [0.3.0] - 2025-11-25 (Service Catalog & Knowledge Base)

### 🚀 New Features
- **Service Catalog:** 8 interactive cards (Application, Email, Hardware, Printer, Software, General, VP Reset, VP Permissions).
- **Knowledge Base:** Search, Recent Articles, Detail view with Problem/Solution structure.
- **Ticket Forms:** Specialized intake forms per request category.

### 🎨 UI & UX Polish
- **Card Hover States:** Card hover states (border accent + subtle shadow transition).
- **Form Layout:** Consistent form layout spacing and field grouping.

### ⚙️ Backend & Architecture
- **Retrieval Logic:** Initial KB retrieval logic through service layer.
- **Form Handling:** Added structured form handling functions in views.

### 🐛 Fixes
- **Template Paths:** Early template path mismatches.
- **Validation:** Validation messages for required form fields.

---

## [0.2.0] - 2025-11-24 (User Experience)

### 🚀 New Features
- **User Dashboard:** Ticket summary metrics + recent tickets table.
- **Ticket Service Layer:** Centralized retrieval and mock ticket generation.
- **Activity Log on Ticket Detail:** Basic chronological comment history.

### 🎨 UI & UX Polish
- **Navigation:** Top navigation standardization.
- **Brand Consistency:** Footer and header consistent brand palette usage.
- **Interactivity:** Hover-enhanced table row interaction.

### ⚙️ Backend & Architecture
- **Service Layer:** Created `ticket_service.py` for ticket stat calculation and aggregation.
- **Data Seeding:** Implemented mock data seeding approach.

### 🐛 Fixes
- **Sorting Stability:** Sorting stability across ticket columns.
- **Rendering:** Session-related template rendering edge cases.

---

## [0.1.0] - 2025-11-23 (Initial Commit)

### 🚀 New Features
- **Project Initialization:** Django project + three core apps (config, service_desk, knowledge_base).
- **Base Routing:** Dashboard root + catalog and KB entry points.
- **Initial Models:** Ticket and Article foundational schemas.

### 🎨 UI & UX Polish
- **Base Layout:** Base Layout (`base.html`) with Tailwind + brand colors.
- **Placeholders:** Early navigation and structural placeholder components.

### ⚙️ Backend & Architecture
- **Settings:** Settings configuration for template directories and installed apps.
- **Migrations:** Migrations applied; superuser creation workflow documented.

### 🐛 Fixes
- **N/A:** (foundation release).

---

## License

© 2025 PRIME AE Group, Inc. Internal use only.