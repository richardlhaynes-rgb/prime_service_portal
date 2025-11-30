# Changelog

All notable changes to the PRIME Service Portal project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.7.0] - 2025-11-29 (System Logs & Final Polish)

### 🚀 New Features
- System Activity Logs: Added full audit trail stored in [data/system_logs.json](data/system_logs.json) (actions: Login, Update, Delete).
- Log Viewer: New System Logs page with search, sorting, and Windows-style timestamps.
- Time Zone Support: Dynamic selector (ET, CT, MT, PT, AKT, HST) converting UTC log entries.
- User Menu: Detached “Windows 11 Style” flyout with name/title and secure POST Sign Out.

### 🎨 UI & UX Polish
- Table Icon Columns: Standardized center-center alignment across Dashboard and KB Manager.
- KB Manager Toolbar: Fixed vertical spacing and padding consistency.

### ⚙️ Backend & Architecture
- Logging Pipeline: Implemented `log_system_event()` in [`services/ticket_service.py`](services/ticket_service.py) enforcing max 500 retained entries.
- System Health Integration: Updated update flow to emit audit entries on changes.
- Time Zone Handling: Added conversion logic at view layer for log timestamps.

### 🐛 Fixes
- CSAT Report: Repaired technician-specific feedback loading.
- KB Manager: Restored search + filter chaining and corrected toolbar layout.

---

## [0.6.0] - 2025-11-28 (The Feature Complete Update)

### 🚀 New Features
- Knowledge Base Editor: Full CRUD for articles (Add, Edit, Delete, Manage).
- Bulk Article Actions: Multi-select with status transitions (Draft, Pending, Approved).
- Management Hub: Central admin launchpad (Analytics, Settings, Logs, KB Manager).
- Scheduled Announcements: Start/End datetime support for system banners.

### 🎨 UI & UX Polish
- Consistent table sorting visuals and icon-only status badges.
- KB Listing: Category sidebar, improved hover states, refined spacing.
- Navigation: Streamlined admin access model; unified header alignment.

### ⚙️ Backend & Architecture
- View Consolidation: Merged KB editor views into [`service_desk/views.py`](service_desk/views.py).
- Data Taxonomy: Normalized KB categories and subcategories (ConnectWise alignment).
- Icon Injection Pipeline: Dynamic icon resolution via mappings in [`services/ticket_service.py`](services/ticket_service.py).
- System Health Enhancements: Added scheduling fields to persisted structure.

### 🐛 Fixes
- Article editor submission errors (import path corrections).
- Technician profile 404 (moved to slug-based routing).
- Announcement scheduling persistence.
- KB icon fallback elimination (all mapped).

---

## [0.5.0] - 2025-11-27 (Architecture Sprint)

### 🚀 New Features
- Global System Health Banner: Slim status bar with vendor dropdown.
- Admin CMS: `/manager/settings/` for modifying announcements + vendor statuses.
- Ticket Survey: CSAT form workflow (star rating demo implementation).

### 🎨 UI & UX Polish
- Dashboard tables modernized (hover rows, icon column alignment).
- Manager analytics visual adjustments (stable chart heights).
- Service Catalog grid final styling pass.

### ⚙️ Backend & Architecture
- Context Processor: Injected system health globally.
- Technician Roster: Migrated to URL-safe slug IDs (e.g., `richard_haynes`).
- Demo Mode Pattern: Centralized mock retrieval through service layer toggle (`USE_MOCK_DATA`).

### 🐛 Fixes
- Chart overflow growth bug.
- Dropdown close behavior and minor survey persistence issues.
- Broken profile links due to space-containing identifiers.

---

## [0.4.0] - 2025-11-26 (Manager Analytics)

### 🚀 New Features
- Manager Dashboard: Added Chart.js widgets (Volume by Status, Tickets by Type, Trend, Resolution Time).
- Technician Profiles: Individual performance views (open tickets, CSAT, recent activity).
- Team Roster: Grid layout with dynamic open ticket badges.

### 🎨 UI & UX Polish
- Introduced hero banners for technician profiles.
- Refined analytics cards and consistent spacing for metric sections.

### ⚙️ Backend & Architecture
- Expanded analytics data model in [`services/ticket_service.py`](services/ticket_service.py).
- Generated technician roster records with stats and feedback arrays.

### 🐛 Fixes
- Minor sorting inconsistencies on manager views.
- Profile navigation reliability across roster IDs.

---

## [0.3.0] - 2025-11-25 (Service Catalog & Knowledge Base)

### 🚀 New Features
- Service Catalog: 8 interactive cards (Application, Email, Hardware, Printer, Software, General, VP Reset, VP Permissions).
- Knowledge Base: Search, Recent Articles, Detail view with Problem/Solution structure.
- Ticket Forms: Specialized intake forms per request category.

### 🎨 UI & UX Polish
- Card hover states (border accent + subtle shadow transition).
- Consistent form layout spacing and field grouping.

### ⚙️ Backend & Architecture
- Initial KB retrieval logic through service layer.
- Added structured form handling functions in views.

### 🐛 Fixes
- Early template path mismatches.
- Validation messages for required form fields.

---

## [0.2.0] - 2025-11-24 (User Experience)

### 🚀 New Features
- User Dashboard: Ticket summary metrics + recent tickets table.
- Ticket Service Layer: Centralized retrieval and mock ticket generation.
- Activity Log on Ticket Detail: Basic chronological comment history.

### 🎨 UI & UX Polish
- Top navigation standardization.
- Footer and header consistent brand palette usage.
- Hover-enhanced table row interaction.

### ⚙️ Backend & Architecture
- Created `ticket_service.py` for ticket stat calculation and aggregation.
- Implemented mock data seeding approach.

### 🐛 Fixes
- Sorting stability across ticket columns.
- Session-related template rendering edge cases.

---

## [0.1.0] - 2025-11-23 (Initial Commit)

### 🚀 New Features
- Project Initialization: Django project + three core apps (config, service_desk, knowledge_base).
- Base Routing: Dashboard root + catalog and KB entry points.
- Initial Models: Ticket and Article foundational schemas.

### 🎨 UI & UX Polish
- Base Layout (`base.html`) with Tailwind + brand colors.
- Early navigation and structural placeholder components.

### ⚙️ Backend & Architecture
- Settings configuration for template directories and installed apps.
- Migrations applied; superuser creation workflow documented.

### 🐛 Fixes
- N/A (foundation release).

---

## License

© 2025 PRIME AE Group, Inc. Internal use only.