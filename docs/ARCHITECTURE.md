PRIME Service Portal - Architecture Overview

1. High-Level Concept

The PRIME Service Portal is a monolithic Django web application designed to serve as the internal "One-Stop-Shop" for IT support. It replaces the legacy ConnectWise portal with a modern, responsive interface.

Framework: Django 5.x (Python)

Frontend: HTML5 + Tailwind CSS (via CDN for Prototyping)

Database: SQLite (Local Prototype) -> Azure SQL (Future Production)

Authentication: Native Django Auth -> Azure AD (Future)

2. Application Modules (Django Apps)

The project is split into logical domains to ensure separation of concerns:

A. config (The Project Root)

Holds global configurations (settings.py).

Controls the main URL routing (urls.py).

Configures the WSGI/ASGI entry points for server deployment.

B. core (The UI/UX Engine)

Responsibility: Manages shared layouts, the dashboard (Homepage), and navigation logic.

Key Files: views.py (renders the home page).

C. service_desk (The Ticket Engine) - [Planned]

Responsibility: Will handle Ticket creation, API calls to ConnectWise Manage, and Service Catalog logic.

Future State: Will contain models.py for caching ticket data and api.py for external communication.

D. knowledge_base (The Library) - [Planned]

Responsibility: Will handle articles, FAQs, and search functionality.

3. Design System

Framework: Tailwind CSS (Utility-First).

Brand Identity:

Navy: #003E52 (Header, Primary Text)

Flamingo Orange: #F15C2B (Accents, Buttons, Hovers)

Forest Green: #0F5838 (Success States)

4. Deployment Strategy

Current: Localhost (Windows 11).

Target: Azure App Service (Linux Container).

CI/CD: GitHub Actions -> Azure Deployment.

Architected by: Richard Haynes & The AI Architect