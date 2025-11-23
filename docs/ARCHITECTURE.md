PRIME Service Portal - Architecture Overview

Last Updated: November 21, 2025

1. High-Level Concept

The PRIME Service Portal is a centralized, web-based dashboard for IT support. It replaces the legacy ConnectWise Manage portal with a modern, responsive interface designed for speed and clarity.

Core Philosophy: "Dashboard First." Users land immediately on their status overview, reducing anxiety and clicks.

Framework: Django 5.x (Python).

Frontend: HTML5 + Tailwind CSS (Utility-First design system).

Database: SQLite (Prototype) -> Azure SQL (Production).

Authentication: Native Django Auth (Phase 1) -> Azure AD / SSO (Future Phase).

2. System Architecture

The project is a monolithic Django application split into three logical domains ("Apps"):

A. config (The Root)

Role: The project brain. Handles global settings, middleware, and the master URL routing map.

Key File: urls.py (Maps / to Dashboard, /catalog/ to Service Catalog, /kb/ to Knowledge Base).

B. service_desk (The Engine)

Role: Manages the core IT workflows: Ticket submission, Dashboard logic, and Form processing.

Key Components:

models.py: Defines the Ticket database schema.

forms.py: Contains the 8 specific forms (Application, Email, Hardware, etc.) with conditional logic.

views.py: Handles the business logic for the Dashboard stats (open_tickets, resolved_tickets) and form processing.

C. knowledge_base (The Library)

Role: Manages self-service articles to deflect tickets.

Design: Mirrors the ConnectWise Manage schema for future synchronization.

Key Components:

models.py: Defines the Article schema (Category, Problem, Solution).

views.py: Handles search logic (kb_home) and article display (article_detail).

3. The User Journey (Navigation Flow)

Landing (/): The Dashboard.

Goal: Instant status visibility.

Features: Welcome Banner, System Status, Ticket Stats, Recent History table.

Action (/catalog/): The Service Catalog.

Goal: Triage the user's request.

Features: 8-Card Grid layout directing users to specific forms.

Submission (/report/...): The Forms.

Goal: Capture structured data.

Features: tailored fields (e.g., "Computer Name", "Error Message") that map to a standard Ticket.

Self-Help (/kb/): The Knowledge Base.

Goal: Solve problems without a ticket.

Features: Search bar, Recent Articles list, detailed Article view.

4. Deployment Strategy

Current State: Local Development (Windows 11 + VS Code).

Source Control: GitHub (Private Repo).

Future Target: Azure App Service (Containerized).

Architected by: Richard Haynes & The AI Architect