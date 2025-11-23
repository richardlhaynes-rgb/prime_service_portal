PRIME Service Portal - Developer Guide

Version: 1.2.0

Last Updated: November 21, 2025

Maintainer: Richard Haynes (Internal IT)

1. Introduction

This manual details the setup, operation, and maintenance of the PRIME Service Portal development environment. It is designed to allow a new developer (or a reset machine) to go from "Zero" to "Live Server" in under 15 minutes.

2. Prerequisites (The Toolbelt)

Ensure the host machine has the following installed:

Python 3.12+ (Download)

Critical: Check "Add python.exe to PATH" during install.

Git for Windows (Download)

Settings: Default options are fine.

Visual Studio Code (Download)

Recommended Extensions: Python, Django, Tailwind CSS IntelliSense, Black Formatter.

3. Installation (Rebuilding from Scratch)

3.1. Clone the Repository

Open PowerShell/Terminal in your desired projects folder (C:\Projects\):

git clone [https://github.com/YOUR_USERNAME/prime_service_portal.git](https://github.com/YOUR_USERNAME/prime_service_portal.git)
cd prime_service_portal


3.2. Environment Setup (One-Time)

Create Virtual Environment:

python -m venv venv


Activate Environment:

.\venv\Scripts\Activate


Install Dependencies:

pip install django


3.3. Database Initialization

Apply Migrations (Creates tables for Tickets and KB Articles):

python manage.py migrate


Create Admin User (For accessing /admin):

python manage.py createsuperuser


3.4. Data Seeding (Optional but Recommended)

To populate the dashboard and KB with realistic demo data immediately:

Seed Knowledge Base:

python manage.py import_kb


(Reads from kb_source.md in the root folder)

Seed Tickets:

python manage.py populate_tickets


4. Daily Workflow

Method A: The "One-Click" Launcher

Double-click the run_portal.bat file in the project root. This opens a terminal, activates the environment, and starts the server automatically.

Method B: Manual Start

Open VS Code in the project folder.

Open Terminal (Ctrl +  `).

Run:

.\venv\Scripts\Activate
python manage.py runserver


Access the site at: http://127.0.0.1:8000/

5. Project Structure

config/: Main settings and global URL map.

service_desk/: Core app. Contains models.py (Ticket schema), forms.py (8 Service Cards), and views.py (Dashboard logic).

knowledge_base/: KB app. Contains Article model and search logic.

templates/: HTML files.

base.html: Master layout (Header/Nav/Footer).

dashboard.html: The homepage.

service_catalog.html: The grid of 8 cards.

kb_source.md: The master content file for Knowledge Base articles.

6. Troubleshooting

"NoReverseMatch" Error: Usually means a template is linking to a URL name that hasn't been defined in urls.py. Check config/urls.py to ensure apps are included.

Missing CSS/Styles: Ensure your computer is online. Tailwind CSS is loaded via CDN.