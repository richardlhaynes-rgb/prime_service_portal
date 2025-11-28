# Changelog

All notable changes to the "PRIME Service Portal" project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### 🔮 Planned Features
- [ ] ConnectWise Manage API integration (Live Data mode)
- [ ] Azure AD SSO authentication
- [ ] Email notifications for ticket updates
- [ ] Mobile-responsive views
- [ ] Real CSAT feedback storage
- [ ] Ticket attachment upload functionality
- [ ] Executive reporting dashboard

---

## [0.6.0] - 2025-11-28 - **The Feature Complete Update**

### 🚀 New Features

#### **Knowledge Base Editor (Full CRUD)**
- **KB Manager Dashboard** ([`/service-desk/manager/kb/`](service_desk/views.py)):
  - Bulk edit table showing all KB articles
  - Sortable columns: ID, Title, Category, Status, Last Updated
  - Quick action buttons: Edit, Delete
  - "Add New Article" button (top-right)
- **KB Add Form** ([`/service-desk/kb/add/`](service_desk/views.py)):
  - Category dropdown (7 main categories)
  - Subcategory dropdown (34 ConnectWise subcategories)
  - Problem/Solution textareas
  - Internal Notes field (IT-only)
  - Status selector (Draft, Pending, Approved)
- **KB Edit Form** ([`/service-desk/kb/edit/<id>/`](service_desk/views.py)):
  - Pre-filled with existing article data
  - Same fields as Add form
  - Success message: "✅ Article Updated"
- **KB Delete Confirmation** ([`/service-desk/kb/delete/<id>/`](service_desk/views.py)):
  - Shows article title and metadata
  - "Confirm Delete" button (red, destructive)
  - "Cancel" button returns to KB Manager

#### **Admin Toolbar (Article Detail Enhancement)**
- **Toolbar Location**: Top-right of [`templates/knowledge_base/article_detail.html`](templates/knowledge_base/article_detail.html)
- **Buttons** (Superusers only):
  - **Edit Article**: Orange button, pencil icon, links to Edit form
  - **Delete Article**: Red button, trash icon, links to Delete confirmation
- **Permissions**: Toolbar hidden for non-superusers (`{% if request.user.is_superuser %}`)

#### **Scheduled Announcements (System Health CMS)**
- **New Fields** in [`/service-desk/manager/settings/`](service_desk/views.py):
  - **Start Time**: Datetime input (`type="datetime-local"`)
  - **End Time**: Datetime input (`type="datetime-local"`)
- **Use Case**: Schedule maintenance announcements to auto-display during specific windows
- **Data Storage**: Saved to [`data/system_health.json`](data/system_health.json):
  ```json
  {
    "announcement": {
      "title": "Scheduled Maintenance",
      "message": "VPN will be down 8-10 PM EST",
      "type": "Alert",
      "start_datetime": "2025-11-28T20:00",
      "end_datetime": "2025-11-28T22:00"
    }
  }
  ```

#### **Management Hub (Admin Launchpad)**
- **Route**: [`/service-desk/manager/hub/`](service_desk/views.py)
- **Purpose**: Central dashboard for manager-level actions
- **Card Grid** (3 cards):
  1. **Analytics Dashboard**: Links to Manager Dashboard with chart icon
  2. **System Settings**: Links to Admin Settings with cog icon
  3. **Knowledge Base Manager**: Links to KB Manager with book icon
- **Design**: Orange accent cards with hover effects

#### **Dependent Dropdown (KB Editor Enhancement)**
- **Javascript Logic** in [`templates/knowledge_base/kb_form.html`](templates/knowledge_base/kb_form.html):
  - When Category changes, Subcategory dropdown filters to show only relevant options
  - Example: Selecting "Design Applications" → Shows "Adobe", "Autodesk", "Bluebeam", etc.
  - Prevents invalid combinations (e.g., "Autodesk" under "Printing")
- **Mapping**:
  ```javascript
  const subcategoryMap = {
    'Design Applications': ['Adobe Creative Suite', 'Autodesk', 'Bluebeam', ...],
    'Hardware & Peripherals': ['Workstations', 'Mobile Devices', 'Monitors', ...],
    ...
  }
  ```

### 🎨 UI & UX

#### **Knowledge Base Visual Redesign**
- **Strict Icon Mapping System**: 34 unique Heroicons mapped to exact ConnectWise subcategories
  - Autodesk → Cube (3D wireframe)
  - Microsoft 365 → Squares 2x2 (grid)
  - VPN / Remote Access → Lock (padlock)
  - Workstations → Computer Desktop
  - Bluebeam → Document with magnifying glass
  - Conference Room AV → Speaker
  - Specialty Peripherals → Cursor with rays
  - Full mapping in [`services/ticket_service.py`](services/ticket_service.py) `SUBCATEGORY_ICONS` dictionary
- **2-Column Layout**:
  - Left sidebar (1/4 width) for category navigation
  - Right content area (3/4 width) for article list
- **Hover Effects**: Icons transition from gray to orange, entire row highlights

#### **CSAT Report Redesign**
- **Date Range Controls**:
  - Preset Buttons: Today, Yesterday, Last 7 Days, Last 30 Days, Custom Range
  - Swap Mode: Clicking "Custom Range" replaces buttons with inline date inputs
  - Active state management (orange button highlight)
- **Feedback List**:
  - Visual star ratings (★★★★★)
  - User avatar, ticket number, comment text
  - Timestamp ("2 hours ago")
- **Technician Filter Dropdown**: Filter feedback by assigned technician

#### **Navigation Updates**
- **Top Nav Bar**:
  - **Old**: Dashboard | Service Catalog | Knowledge Base | Analytics
  - **New**: Dashboard | Service Catalog | Knowledge Base | Admin ▼
- **Admin Dropdown Menu**:
  - Management Hub
  - Analytics Dashboard
  - System Settings
  - Knowledge Base Manager
- **Permissions**: Admin menu only visible to superusers

#### **User Dashboard Modernization**
- **Icon-Only Status Badges**: Visual indicators with no text clutter
  - Blue star → New
  - Yellow hourglass → In Progress
  - Green checkmark → Resolved
  - Gray archive box → Closed
- **Chevron Navigation**: Right-pointing arrow replaces "View Ticket" button
- **Hover Effects**: Entire row highlights, icons turn orange

### ⚙️ Backend

#### **View Consolidation**
- **Problem**: Import errors (`knowledge_base.views` missing `kb_add`, `kb_edit`, `kb_delete`)
- **Solution**: Moved all KB editor views from [`knowledge_base/views.py`](knowledge_base/views.py) to [`service_desk/views.py`](service_desk/views.py)
- **Impact**: Fixed 500 errors when clicking "Add Article" or "Edit" buttons

#### **Data Taxonomy Overhaul**
- **Complete Rewrite** of [`data/mock_articles.json`](data/mock_articles.json):
  - 45 professional articles across 7 categories
  - Subcategories now use exact verbose strings from ConnectWise:
    - `"Autodesk (AutoCAD, Revit, Civil 3D)"`
    - `"Microsoft 365 (Office, Teams, OneDrive)"`
    - `"Workstations (Desktops, Laptops)"`
    - `"Mobile Devices (iPhones, iPads)"`
  - Zero placeholder data (no "Foo/Bar" examples)
  - Full metadata: `id`, `title`, `category`, `subcategory`, `problem`, `solution`, `status`, timestamps

#### **Service Layer Enhancements**
- **Icon Injection Pipeline** in [`services/ticket_service.py`](services/ticket_service.py):
  - `_get_icon_for_article(article)`: Returns Heroicon name based on subcategory
  - `get_knowledge_base_articles()`: Injects `article['icon']` property before template rendering
  - 3-tier lookup logic:
    1. Exact subcategory match (`SUBCATEGORY_ICONS`)
    2. Fallback to category-level icon (`CATEGORY_ICONS`)
    3. Default to `'document-text'` (generic)
- **CRUD Functions**:
  - `create_kb_article(article_data)`: Appends to mock JSON and assigns next ID
  - `update_kb_article(article_id, updated_data)`: Finds and replaces article in JSON
  - `delete_kb_article(article_id)`: Removes article from JSON array
- **Date Filtering** in `get_dashboard_stats(date_range, start_date, end_date)`:
  - Custom range support via `start_date` and `end_date` parameters
  - Returns filtered analytics data (tickets, feedback, SLA breaches)

#### **Technician Roster Refactor**
- **Problem**: Profile URLs were breaking because tech names contained spaces ("Richard Haynes" → 404)
- **Solution**: Updated `STAFF_ROSTER` dictionary to use URL-safe IDs as keys:
  ```python
  STAFF_ROSTER = {
      "richard_haynes": {...},  # Was: "Richard Haynes"
      "rob_german": {...},      # Was: "Rob German"
      ...
  }
  ```
- **Impact**: All profile links now use slug-based routing (`/manager/technician/richard_haynes/`)

### 🐛 Fixes

- **KB Editor Form**: Fixed 500 error when submitting new articles (corrected import path)
- **Manager Dashboard**: Fixed chart overflow bug (charts now render at fixed `h-80` height)
- **Technician Profiles**: Fixed 404 errors on profile links (moved from name-based to ID-based routing)
- **Knowledge Base**: Fixed generic icons (all articles now show category-specific icons)
- **CSAT Report**: Fixed date range persistence (URL parameters now carried through navigation)
- **Admin Settings**: Fixed announcement scheduling (added `start_time` and `end_time` fields)

### 📊 Data Quality

- **Professional Mock Data**: All demo content uses realistic IT scenarios (no "Foo/Bar" placeholder text)
- **Complete Metadata**: All 45 KB articles have full field coverage
- **Consistent Formatting**: Dates in `"Mon DD, YYYY"` format across all views
- **Icon Coverage**: 100% of KB articles have mapped icons (no generic fallbacks in production data)
- **Taxonomy Compliance**: All subcategories match official ConnectWise Source of Truth list

### 🛠️ Technical Improvements

- **Service Layer Consolidation**: All KB data now flows through [`services/ticket_service.py`](services/ticket_service.py)
- **URL-Safe Identifiers**: Tech roster uses slugified IDs for clean, bookmarkable URLs
- **Template Optimization**: Removed debug code from templates (production-ready)
- **Form Validation**: Added Django form validation for all KB editor fields
- **Permissions Enforcement**: All manager-level views check `request.user.is_superuser`

---

## [0.5.1] - 2025-01-15 - **The KB Polish Sprint**

### 🚀 New Features

#### **Knowledge Base Taxonomy Alignment**
- Complete data overhaul to match official ConnectWise subcategories
- Professional article titles (e.g., "AutoCAD: Reset to Default Settings")
- Full metadata coverage

#### **Strict Icon Mapping System**
- Zero guessing - all 34 subcategories have exact icon mappings
- 3-tier lookup logic (exact → category → default)
- Dynamic SVG rendering in templates

### 🎨 UI & UX

- 2-column layout with category sidebar
- Icon-only status badges (star, hourglass, checkmark, archive)
- Hover effects (orange transitions)
- Fixed chart overflow bugs
- Restored compact team roster

### ⚙️ Backend

- Technician roster refactor (URL-safe IDs)
- Icon injection pipeline
- View layer consolidation
- KB data enrichment (45 articles)

---

## [0.5.0] - 2025-11-27 - **The Architecture & Polish Sprint**

### 🚀 New Features

#### **Global System Health Monitoring**
- System Operations Banner (visible on every page)
- Vendor status dropdown (Office 365, Autodesk, Bentley, Egnyte, Bluebeam)
- Context processor injection

#### **Admin CMS (Content Management System)**
- Settings page to update announcements without code deployment
- Vendor status manager with emoji indicators
- Saves to [`data/system_health.json`](data/system_health.json)

#### **Knowledge Base Foundation**
- 2-column layout with category sidebar
- Search functionality (real-time filtering)
- Category icons (dynamic SVG rendering)
- Article detail view (breadcrumb navigation)

#### **Ticket Survey (CSAT Feedback)**
- Public survey form (5-star rating system)
- Demo Mode confirmation message
- Portal-first banner in ticket detail view

### 🎨 UI & UX

- User dashboard enhancements (summary cards, recent tickets table)
- Manager dashboard visuals (date range controls, SLA breach alerts, performance charts)
- Technician profile page (hero banner, stats grid)
- Service catalog grid (8-card layout, hover effects)

### ⚙️ Backend

- Demo mode architecture (`USE_MOCK_DATA = True`)
- Service layer pattern (all data through `ticket_service.py`)
- Mock data storage (tickets, articles, system health)
- Staff roster database (9 team members with feedback)
- Ticket service functions (stats, technician details, KB articles)

### 🐛 Fixes

- Fixed chart overflow
- Fixed custom range button hover state
- Fixed comment form submission in Mock Data mode
- Fixed search query persistence
- Implemented click-outside-to-close for dropdowns

---

## [0.4.0] - 2025-11-26 - **Manager Analytics**

### 🚀 New Features

#### **Manager Dashboard**
- Chart.js visualizations (pie, bar, line charts)
- Date range filters (Today, Yesterday, Last 7 Days, Last 30 Days)
- Summary cards (total tickets, resolution time, escalations)

#### **Technician Profiles**
- Hero banner (avatar, role, location, email)
- Performance stats (open tickets, CSAT score, response time)
- Recent activity timeline

#### **Team Roster**
- 3-column grid with team member cards
- Status badges (Green = 0 open, Yellow = 1-5, Red = 6+)
- Click-through navigation to profiles

### ⚙️ Backend

- Extended `ticket_service.py` with analytics functions
- Created `STAFF_ROSTER` dictionary (9 team members)
- Added manager dashboard and technician profile views

---

## [0.3.0] - 2025-11-25 - **Service Catalog & Knowledge Base**

### 🚀 New Features

#### **Service Catalog**
- 8-card grid layout (Application Issue, Email, Hardware, etc.)
- Heroicons integration (unique SVG for each card)
- Hover effects (orange border, icon color change)

#### **Ticket Submission Forms**
- 8 specialized forms with conditional fields
- Professional templates with Tailwind styling
- Form validation and success messages

#### **Knowledge Base**
- Search bar (real-time filtering)
- Recent articles grid (10 most recent)
- Article detail view (problem/solution sections)

### ⚙️ Backend

- Created `kb_service.py` for article retrieval
- Added form processing views
- Created KB and Service Desk URL routing

---

## [0.2.0] - 2025-11-24 - **User Experience Foundation**

### 🚀 New Features

#### **User Dashboard**
- Summary cards (Open, Resolved, Total tickets)
- Recent tickets table (sortable columns)
- Hover effects (row highlighting)

#### **Ticket Detail View**
- Ticket info card (ID, status, assigned tech)
- Activity log (comment history)
- Reply form (comment input, priority update)

### ⚙️ Backend

- Created `ticket_service.py` (ticket retrieval, stats)
- Created mock ticket data (10+ demo tickets)
- Added dashboard and ticket detail views

### 🎨 UI & UX

- Standardized navigation (top nav bar)
- User profile badge (name, role, avatar)
- Footer (copyright notice)

---

## [0.1.0] - 2025-11-23 - **Project Foundation**

### 🚀 New Features

#### **Project Setup**
- Initialized Django project (`django-admin startproject config .`)
- Created 3 Django apps (core, service_desk, knowledge_base)
- Registered apps in settings
- Configured global template directory

#### **Frontend Configuration**
- Integrated Tailwind CSS via CDN
- Configured PRIME brand colors (orange, navy, green)
- Created master layout ([`templates/base.html`](templates/base.html))

#### **Database**
- Applied initial migrations
- Created superuser account

#### **Developer Tools**
- Created `run_portal.bat` (one-click server startup)
- Created `dev_shell.bat` (quick terminal access)

### ⚙️ Backend

- Created Ticket model (ConnectWise-compatible schema)
- Created Article model
- Created URL routing (master map, service desk routes)

### 🎨 UI & UX

- Built homepage with system status
- Implemented Heroicons (SVG icons)
- Responsive design (mobile-friendly)

### 📝 Documentation

- Created Developer Guide (installation, workflow, troubleshooting)
- Created Architecture doc (system overview, user journey)
- Created Copilot instructions (AI guidelines, design system)

---

## Statistics

### Overall Project Metrics
- **Total Files**: 100+
- **Lines of Code**: ~6,000+
- **Commits**: 6 major milestones
- **Development Time**: 6 days (Nov 23-28, 2025)
- **Developer**: Richard Haynes (Product Owner) + GitHub Copilot (AI Architect)

### Feature Breakdown
- **Views Created**: 20+
- **Templates Created**: 25+
- **Forms Created**: 8 specialized intake forms + KB editor form
- **Management Commands**: 4
- **Mock Data Articles**: 45
- **Mock Data Tickets**: 10+
- **Staff Roster**: 9 team members

---

## Acknowledgments

**Developed by**: Richard Haynes, Service Desk Manager  
**AI Pair Programmer**: GitHub Copilot (Claude Sonnet 4.5)  
**Organization**: PRIME AE Group, Inc. - Information Technology Department  
**Dates**: November 23-28, 2025 (Thanksgiving Week 🦃)

---

## License

© 2025 PRIME AE Group, Inc. All rights reserved.  
Internal use only. Not licensed for distribution.

---

**Last Updated**: November 28, 2025  
**Maintainer**: Richard Haynes (richard.haynes@primeeng.com)