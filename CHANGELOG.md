# Changelog

All notable changes to the PRIME Service Portal project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- Fixed the Management Hub icon link pointing to a non-existent URL name.
- Corrected disjointed hover states in the main navigation header.

---

## [0.10.0] - 2025-12-21 (User Identity & Data Integrity)

### 🚀 New Features
- **Enhanced User Profiles:** Expanded the data model to include **Company**, **Manager**, and **Office Location** fields.
- **Identity Privacy Controls:** Introduced a "Prefer Initials" toggle, allowing users to override their profile photo with a generated avatar.
- **Smart Avatar Engine:** Implemented instant JavaScript previews that update immediately when uploading a file or toggling the "Initials" setting.
- **Expanded Ticket Schema:** Added missing ticket types (`General Question`, `VP Password Reset`, `VP Permissions`) to the database model.

### 🎨 UI & UX Polish
- **"Clean Split" Header Design:** Redesigned the *Edit User* screen with a balanced "Identity vs. Status" layout.
- **Visual Account Stats:** Added right-aligned badges (Active, Staff, Superuser) and "Member Since/Last Login" timestamps to the user header.
- **Instant Feedback:** Avatar previews now react in real-time to user inputs (uploads or checkbox toggles) before saving.
- **Consistent Badging:** Standardized user badges across the User Management list and Edit User screens.

### ⚙️ Backend & Architecture
- **Data Generator Overhaul:** Rewrote `generate_demo_tickets.py` to populate the new profile fields and assign realistic office locations.
- **Status Standardization:** Standardized the ticket workflow to use **"Resolved"** (removing references to the invalid "Closed" status).
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
- Fixed `RelatedObjectDoesNotExist` crash when uploading avatars for older user accounts.
- Resolved "Table already exists" conflicts during taxonomy migration.
- Fixed layout alignment issues where setting panels were not flush with the sidebar.

---

## [0.7.0] - 2025-11-29 (System Logs & Final Polish)

### 🚀 New Features
- **System Activity Logs:** Added full audit trail stored in `data/system_logs.json` (actions: Login, Update, Delete).
- **Log Viewer:** New System Logs page with search, sorting, and Windows-style timestamps.
- **Time Zone Support:** Dynamic selector (ET, CT, MT, PT, AKT, HST) converting UTC log entries.
- **User Menu:** Detached “Windows 11 Style” flyout with name/title and secure POST Sign Out.

### 🎨 UI & UX Polish
- Table Icon Columns: Standardized center-center alignment across Dashboard and KB Manager.
- KB Manager Toolbar: Fixed vertical spacing and padding consistency.

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
- Consistent table sorting visuals and icon-only status badges.
- **KB Listing:** Category sidebar, improved hover states, refined spacing.
- **Navigation:** Streamlined admin access model; unified header alignment.

### ⚙️ Backend & Architecture
- **View Consolidation:** Merged KB editor views into `service_desk/views.py`.
- **Data Taxonomy:** Normalized KB categories and subcategories (ConnectWise alignment).
- **Icon Injection Pipeline:** Dynamic icon resolution via mappings in `services/ticket_service.py`.
- **System Health Enhancements:** Added scheduling fields to persisted structure.

### 🐛 Fixes
- Article editor submission errors (import path corrections).
- Technician profile 404 (moved to slug-based routing).
- Announcement scheduling persistence.
- KB icon fallback elimination (all mapped).

---

## [0.5.0] - 2025-11-27 (Architecture Sprint)

### 🚀 New Features
- **Global System Health Banner:** Slim status bar with vendor dropdown.
- **Admin CMS:** `/manager/settings/` for modifying announcements + vendor statuses.
- **Ticket Survey:** CSAT form workflow (star rating demo implementation).

### 🎨 UI & UX Polish
- Dashboard tables modernized (hover rows, icon column alignment).
- Manager analytics visual adjustments (stable chart heights).
- Service Catalog grid final styling pass.

### ⚙️ Backend & Architecture
- **Context Processor:** Injected system health globally.
- **Technician Roster:** Migrated to URL-safe slug IDs (e.g., `richard_haynes`).
- **Demo Mode Pattern:** Centralized mock retrieval through service layer toggle (`USE_MOCK_DATA`).

### 🐛 Fixes
- Chart overflow growth bug.
- Dropdown close behavior and minor survey persistence issues.
- Broken profile links due to space-containing identifiers.

---

## [0.4.0] - 2025-11-26 (Manager Analytics)

### 🚀 New Features
- **Manager Dashboard:** Added Chart.js widgets (Volume by Status, Tickets by Type, Trend, Resolution Time).
- **Technician Profiles:** Individual performance views (open tickets, CSAT, recent activity).
- **Team Roster:** Grid layout with dynamic open ticket badges.

### 🎨 UI & UX Polish
- Introduced hero banners for technician profiles.
- Refined analytics cards and consistent spacing for metric sections.

### ⚙️ Backend & Architecture
- Expanded analytics data model in `services/ticket_service.py`.
- Generated technician roster records with stats and feedback arrays.

### 🐛 Fixes
- Minor sorting inconsistencies on manager views.
- Profile navigation reliability across roster IDs.

---

## [0.3.0] - 2025-11-25 (Service Catalog & Knowledge Base)

### 🚀 New Features
- **Service Catalog:** 8 interactive cards (Application, Email, Hardware, Printer, Software, General, VP Reset, VP Permissions).
- **Knowledge Base:** Search, Recent Articles, Detail view with Problem/Solution structure.
- **Ticket Forms:** Specialized intake forms per request category.

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
- **User Dashboard:** Ticket summary metrics + recent tickets table.
- **Ticket Service Layer:** Centralized retrieval and mock ticket generation.
- **Activity Log on Ticket Detail:** Basic chronological comment history.

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
- **Project Initialization:** Django project + three core apps (config, service_desk, knowledge_base).
- **Base Routing:** Dashboard root + catalog and KB entry points.
- **Initial Models:** Ticket and Article foundational schemas.

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