# Changelog

All notable changes to the "PRIME Service Portal" project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.2] - 2025-11-17
### Added
- Created Application Architecture:
    - `core`: Main UI and navigation logic.
    - `service_desk`: Ticket and API logic.
    - `knowledge_base`: Documentation engine.
- Registered apps in `config/settings.py`.
- Configured Global Template Directory (`templates/`).
- Created Master Layout (`base.html`) with PRIME branding colors.
- Created Homepage View (`core/views.py`) and URL routing.
- Added `run_portal.bat` for one-click server startup.
- Added `dev_shell.bat` for quick terminal access.
- Integrated Tailwind CSS via CDN.
- Implemented PRIME Brand Colors (Navy/Orange) in Tailwind config.
- Built 8-Card Service Catalog Grid with Heroicons.
- Updated Footer to official corporate standard.

## [0.0.1] - 2025-11-17
### Added
- Initialized project directory `prime_service_portal`.
- Created Virtual Environment (`venv`).
- Installed Django 5.x and Black formatter.
- Configured Project Skeleton using `config` pattern.
- Applied initial SQLite database migrations.
- Created Superuser `richard.haynes`.

## [0.5.0] - 2025-11-27 (The Copilot Sprint)

### 🎯 **Core Architecture**
- **Initialized Django Project** with Tailwind CSS integration via CDN
- **Implemented "Demo Mode" Toggle**: Application operates in Mock Data mode (`USE_MOCK_DATA = True`)
  - Created `services/ticket_service.py` as the centralized data layer
  - Mock data stored in `data/mock_tickets.json`, `data/mock_articles.json`, `data/system_health.json`
  - Future-proofed for ConnectWise Manage API integration (Live Data mode)
- **Service Layer Pattern**: All views fetch data through `ticket_service.py` and `kb_service.py`
- **Context Processor**: Added `system_health_context()` to inject global system status into all templates

---

### 👤 **User Experience (End User)**

#### **Dashboard (`/`)**
- **User Dashboard** (`dashboard.html`):
  - Summary Cards: Open Tickets, Resolved Tickets, Total History
  - "My Recent Tickets" table with sortable columns (ID, Title, Type, Status, Priority, Date)
  - Icon-only status indicators (Blue = New, Yellow = In Progress, Green = Resolved, Gray = Closed)
  - Chevron-style "View Ticket" navigation
  - Link to Service Catalog and Knowledge Base

#### **Service Catalog (`/service-desk/catalog/`)**
- **8-Card Grid Layout** (`service_catalog.html`):
  1. Application Issue
  2. Email & Mailbox
  3. Hardware Issue
  4. Printer & Scanner
  5. Software Install
  6. General IT Question
  7. VP Password Reset
  8. VP Permissions Request
- Heroicons SVG integration for all cards
- Hover effects with orange accent border

#### **Ticket Submission Forms**
- **8 Specialized Forms** (`service_desk/forms.py`):
  - Application Issue (with dropdown + "Other" field)
  - Email & Mailbox (with issue type selection)
  - Hardware Issue (with asset tag tracking)
  - Printer & Scanner (location-based)
  - Software Install (with license info capture)
  - General IT Question (catch-all)
  - VP Password Reset (Deltek-specific)
  - VP Permissions Request (project access management)
- Form Views (`service_desk/views.py`):
  - All forms POST to create `Ticket` objects in database
  - Success messages with ticket confirmation
  - Redirect to Dashboard after submission

#### **Ticket Detail View (`/service-desk/ticket/<id>/`)**
- **Ticket Info Card**: ID, Status, Title, Created Date, Type, Assigned Technician
- **Description Section**: Formatted text in monospace font with pre-wrap
- **Activity Log**: Comment history with author avatars
- **Action Panel** (Right Column):
  - Demo Mode warning banner
  - Reply form (comment + priority update)
  - "Close Ticket" checkbox
  - "Submit Reply" button

#### **Knowledge Base (`/kb/`)**
- **KB Home** (`kb_home.html`):
  - Search bar with real-time query filtering
  - Recent Articles grid (10 most recent)
  - Category badges with color coding
  - Click-through to article detail
- **Article Detail** (`article_detail.html`):
  - Breadcrumb navigation (KB Home → Category → Article)
  - **Problem Section**: Issue description
  - **Solution Section**: Step-by-step resolution
  - **"Was This Helpful?" Widget**:
    - Yes/No buttons (non-functional in Demo Mode)
    - Green checkmark + "Thanks for your feedback!" confirmation
    - Red X + "Sorry to hear that. We'll improve this article."

#### **Ticket Survey (`/service-desk/survey/<id>/`)**
- **Public CSAT Feedback Form**:
  - 5-star rating system (radio buttons)
  - Comment textarea
  - "Submit Feedback" button
  - Demo Mode: Displays confirmation message without saving
- **Portal-First Banner** (Ticket Detail):
  - "Before You Call..." prompt
  - Links to KB and Service Catalog
  - Orange CTA button

---

### 👨‍💼 **Manager Experience (Admin)**

#### **Manager Dashboard (`/service-desk/manager/`)**
- **Date Range Filters**:
  - Preset Buttons: Today, Yesterday, Last 7 Days, Last 30 Days
  - **Custom Range Picker** (Swap-Mode):
    - Clicking "Custom Range" **replaces** button row with inline date inputs
    - "From" and "To" date pickers with "Apply" and "Cancel" buttons
    - Zero vertical layout shift (seamless UI swap)
    - Active state management (Orange button when selected)
- **Summary Cards** (4-Column Grid):
  1. Total Tickets (Blue accent)
  2. Avg Resolution Time (Green accent)
  3. First Response Time (Purple accent)
  4. Priority Escalations (Red accent)
- **Priority Attention Required** (SLA Breach Alert):
  - Red banner with warning icon
  - List of tickets exceeding response time thresholds
  - Ticket ID, title, age (hours), assigned technician
- **Service Desk Team Roster** (3-Column Grid):
  - Team member cards with avatar, name, role
  - Status badge: Green (0 open), Yellow (1-5 open), Red (6+ open)
  - Click-through to Technician Profile
- **Performance Charts** (2x2 Grid):
  1. **Volume by Status** (Pie Chart): Open, In Progress, Resolved, Closed
  2. **Tickets by Category** (Bar Chart): Hardware, Software, Email, etc.
  3. **Trend Analysis** (Line Chart): Time-series ticket volume
  4. **Avg Resolution Time by Technician** (Horizontal Bar Chart)
- **Chart.js Integration**:
  - All charts responsive (`maintainAspectRatio: false`)
  - Fixed height containers (`h-80` = 320px)
  - Brand colors applied (Orange, Navy, Green)

#### **Technician Profile (`/service-desk/manager/technician/<name>/`)**
- **Hero Banner** (Prime Navy background):
  - Large avatar with name, role, location, email
  - Quick Stats: Open Tickets, Resolved This Month, CSAT Score, Avg Response Time
- **Recent Activity Section**:
  - Timeline-style list of recent actions
  - Gray background cards with timestamps
- **Back to Manager Dashboard** link

#### **CSAT Report (`/service-desk/manager/csat/`)**
- **Customer Satisfaction Dashboard**:
  - Average rating display (e.g., "4.8/5")
  - Recent feedback list with user quotes
  - Ticket references and star ratings
  - "Under Construction" banner (future feature)

#### **Admin Settings (`/service-desk/manager/settings/`) 🆕**
- **System Health CMS** (Content Management System):
  - **Global Announcement Manager**:
    - Title input
    - Message textarea
    - Type dropdown (Info, Alert, Success)
    - Live preview of banner appearance
  - **Vendor Status Manager**:
    - Dynamic form fields (Add/Remove vendor rows)
    - Vendor Name input
    - Status dropdown (Operational, Degraded Performance, Outage)
  - **Save to JSON**: Updates `data/system_health.json` without code deployment
  - **Real-Time Updates**: Changes appear in global status bar immediately
- **Permissions**: Only accessible to superusers (`request.user.is_superuser`)

---

### 🌐 **Global Features**

#### **System Health Bar (`base.html`)**
- **Left Section**: Global announcement with megaphone icon
  - Expandable "Read More" toggle for long messages
  - Color-coded based on type (Blue = Info, Yellow = Alert, Red = Critical, Green = Success)
- **Right Section**: Service Status dropdown
  - Overall health badge (Green = All Operational, Yellow = Degraded, Red = Outage)
  - Dropdown list of vendor statuses (Office 365, Autodesk, Bentley, etc.)
  - Click-outside-to-close functionality
- **Data Source**: `system_health_context()` injects `system_health` variable into all pages

#### **Navigation Bar**
- **Logo + Title**: "PRIME AE | Service Portal"
- **Nav Links**:
  - My Dashboard
  - Catalog
  - Knowledge Base
  - Manager (Admin Only, with chart icon)
- **User Profile Badge**: Name, role, avatar
- **Settings Gear Icon**: Links to `/service-desk/manager/settings/` (Admin CMS)

#### **Footer**
- Copyright notice: "© 2025 PRIME AE Group, Inc. - Information Technology"

---

### 📊 **Data & Services**

#### **Ticket Service (`services/ticket_service.py`)**
- **Functions**:
  - `get_all_tickets(user=None)`: Returns ticket list (filtered by user in Live Mode)
  - `get_ticket_stats(tickets)`: Calculates open, resolved, total counts
  - `get_ticket_by_id(ticket_id)`: Single ticket retrieval
  - `get_dashboard_stats(date_range, start_date, end_date)`: Manager analytics data
  - `get_technician_details(tech_id)`: Technician profile data
  - `update_system_health(new_data)`: Saves CMS changes to JSON
- **Mock Data**:
  - 10+ demo tickets with realistic titles ("Outlook Crashing", "VPN Connection Issue")
  - 9 staff roster members with avatars, stats, and recent activity
  - System health data with 6 vendor statuses

#### **KB Service (`services/kb_service.py`)**
- **Functions**:
  - `get_all_articles(search_query=None)`: Returns article list with optional search
  - `get_article_by_id(pk)`: Single article retrieval
- **Mock Data**:
  - Professional articles (e.g., "Outlook: Create a New Profile", "VPN: Troubleshooting")
  - Category classification (Business Software, Design Apps, Networking, etc.)

---

### 🎨 **Design System**

#### **Brand Colors (Tailwind Config)**
- **Prime Orange**: `#F15C2B` (Buttons, CTAs, Active States)
- **Prime Navy**: `#003E52` (Headers, Navigation)
- **Prime Green**: `#0F5838` (Success indicators)
- **Functional Colors**:
  - Jade (`#00ad72`): Resolved tickets
  - Turquoise (`#00a3bc`): Info links
  - Dandelion (`#ffc63e`): Warnings

#### **Component Standards**
- **Cards**: `bg-white rounded-lg shadow-sm border border-gray-100`
- **Buttons**: `bg-prime-orange text-white rounded-md hover:bg-opacity-90`
- **Heroicons**: Outline style, `h-6 w-6` or `h-8 w-8`

---

### 🛠️ **Technical Improvements**

- **Context Processor**: `service_desk/context_processors.py` injects system health globally
- **Management Commands**:
  - `populate_tickets`: Seeds demo ticket data
  - `populate_kb`: Seeds demo KB articles
  - `import_kb`: Parses `kb_source.txt` into Article objects
  - `parse_kb_txt`: Converts markdown-style KB source into JSON
- **URL Routing**:
  - `/` → User Dashboard
  - `/service-desk/catalog/` → Service Catalog
  - `/service-desk/report/*` → Ticket Forms
  - `/service-desk/ticket/<id>/` → Ticket Detail
  - `/service-desk/survey/<id>/` → CSAT Survey
  - `/service-desk/manager/` → Manager Dashboard
  - `/service-desk/manager/settings/` → Admin Settings
  - `/service-desk/manager/technician/<name>/` → Tech Profile
  - `/kb/` → Knowledge Base Home
  - `/kb/article/<id>/` → Article Detail

---

### 📝 **Documentation**

- **Developer Guide** (`docs/DEVELOPER_GUIDE.md`):
  - Installation instructions
  - Daily workflow (one-click launcher vs. manual start)
  - Troubleshooting section
- **Architecture Overview** (`docs/ARCHITECTURE.md`):
  - High-level concept and philosophy
  - System architecture (3 Django apps: `core`, `service_desk`, `knowledge_base`)
  - User journey flow
- **Copilot Instructions** (`.github/copilot-instructions.md`):
  - Identity and protocol (Senior Developer AI, Product Owner: Richard Haynes)
  - Visual design system (brand colors, typography)
  - Component standards (Heroicons, cards, buttons)
  - "Demo Mode" strategy
  - Operational workflow

---

### 🐛 **Bug Fixes & Refinements**

- **Manager Dashboard**:
  - Fixed "Custom Range" button hover state (now stays orange when active)
  - Aligned date picker to right side of header
  - Compacted input row (reduced padding from `p-4` to `p-2`)
  - Implemented swap-mode behavior (buttons vanish, inputs appear in same spot)
- **Ticket Detail**:
  - Added Demo Mode warning banner
  - Fixed comment form submission in Mock Data mode
- **Knowledge Base**:
  - Fixed search query persistence in URL
  - Added "No results found" message for empty searches
- **System Health Bar**:
  - Implemented click-outside-to-close for vendor status dropdown
  - Fixed announcement expand/collapse toggle

---

### 🔒 **Security & Permissions**

- **Manager Dashboard**: Requires `is_superuser = True`
- **Admin Settings**: Requires `is_superuser = True`
- **Ticket Detail**: Users can only view their own tickets (in Live Mode)
- **CSRF Protection**: All forms include `{% csrf_token %}`

---

### 📦 **Dependencies**

- **Django**: 5.x
- **Tailwind CSS**: 3.x (CDN)
- **Chart.js**: 4.x (CDN)
- **Heroicons**: SVG (inline)

---

### 🚀 **Deployment Readiness**

- **Database**: SQLite (dev) → Azure SQL (production)
- **Environment**: Local (Windows 11 + VS Code) → Azure App Service (containerized)
- **Authentication**: Native Django Auth → Azure AD / SSO (future)

---

### 📈 **Statistics**

- **Total Files Modified/Created**: 50+
- **Lines of Code**: ~3,500
- **Commits**: 1 (this Sprint consolidation commit)
- **Developer**: Richard Haynes (Product Owner) + GitHub Copilot (AI Pair Programmer)

---

### 🎉 **Notable Achievements**

1. **Zero-to-MVP in 4 Days**: Fully functional portal with User Dashboard, Manager Analytics, and Admin CMS
2. **Professional Demo Mode**: Mock data quality rivals production systems
3. **Chart.js Integration**: Real-time analytics with responsive, brand-aligned visualizations
4. **Swap-Mode Date Picker**: Innovative UX pattern (button row transforms into input row with zero layout shift)
5. **System Health CMS**: Non-technical admins can update global announcements without code deployment

---

### 🔮 **Next Steps (Backlog)**

- [ ] Integrate ConnectWise Manage API (Live Data mode)
- [ ] Implement Azure AD SSO authentication
- [ ] Add email notifications for ticket updates
- [ ] Build mobile-responsive views
- [ ] Implement real CSAT feedback storage
- [ ] Add ticket attachment upload functionality
- [ ] Create reporting dashboard for executives

---

**Signed:** Richard Haynes, Service Desk Manager  
**Approved by:** GitHub Copilot (AI Architect)  
**Date:** November 27, 2025 (Thanksgiving Day 🦃)