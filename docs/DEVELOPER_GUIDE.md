PRIME Service Portal - Developer Guide

Version: 1.0.0

Last Updated: November 18, 2025

Maintainer: Richard Haynes (Internal IT)

1. Introduction

This document serves as the comprehensive reference manual for the PRIME Service Portal. It contains precise instructions to rebuild the development environment from scratch on a fresh Windows machine, ensuring business continuity and standardized development practices.

Target Audience: IT Staff, Developers, Future Maintainers.

2. Prerequisites (The Toolbelt)

Before creating the project files, ensure the host machine has the following installed. These tools form the foundation of the development environment.

2.1. Required Software

Python 3.12+

Role: The Backend Runtime. Python is the programming language that powers Django, our web framework.

Download: python.org

CRITICAL: During installation, check the box "Add python.exe to PATH".

Git for Windows

Role: Version Control. Git tracks every change made to the code, allowing us to revert errors and manage project history.

Download: git-scm.com

Settings: Default settings are acceptable.

Visual Studio Code (VS Code)

Role: The Integrated Development Environment (IDE). This is the editor where code is written. It was chosen for its robust ecosystem of extensions that support Python and web development.

Download: code.visualstudio.com

Extensions:

Python (Microsoft): Provides debugging and IntelliSense.

Django (Baptiste Darthenay): Provides syntax highlighting for Django templates.

Tailwind CSS IntelliSense: Provides auto-completion for design classes.

Black Formatter (Microsoft): Automatically formats code to meet PEP8 industry standards.

3. Installation (Rebuilding from Scratch)

3.1. File Placement

Create a folder on the local drive (Avoid OneDrive/Network Shares):

Path: C:\Projects\prime_service_portal

If restoring from a ZIP backup:

Extract all contents into this folder.

If restoring from Git:

cd C:\Projects
git clone <repository_url> prime_service_portal


3.2. Environment Setup

Open PowerShell and run these commands inside the project folder (C:\Projects\prime_service_portal):

Create the Virtual Environment (Sandbox):

python -m venv venv


Activate the Environment:

.\venv\Scripts\Activate


(Verify you see (venv) in green on the left).

Install Dependencies:

python -m pip install --upgrade pip
pip install django black


Initialize the Database:

python manage.py migrate


Create an Admin User:

python manage.py createsuperuser
# Follow prompts for username/password


4. Running the Application

Method A: The "One-Click" Launcher (Preferred)

Open File Explorer to C:\Projects\prime_service_portal.

Double-click run_portal.bat.

A black window will open, and the browser should launch to http://127.0.0.1:8000/.

Method B: Manual Launch (PowerShell)

Open PowerShell.

Navigate: cd C:\Projects\prime_service_portal

Activate: .\venv\Scripts\Activate

Run: python manage.py runserver

5. The Admin Interface (Back Office)

Django provides a built-in administrative interface for managing users and database records.

URL: http://127.0.0.1:8000/admin

Login: Use the Superuser credentials created in Step 3.2.

Design Note: The Admin Interface uses default Django styling (Navy/Blue). It does not inherit the custom PRIME Service Portal theme (Tailwind CSS). This is intentional behavior.

6. Project Structure (Where things live)

prime_service_portal/
├── config/                 # The "Brain" (Global Settings, URL Routing)
│   ├── settings.py         # Apps, Database, & Template config
│   └── urls.py             # Master traffic controller
│
├── core/                   # The "Manager" App
│   └── views.py            # Homepage logic
│
├── templates/              # HTML Files (The Visuals)
│   ├── base.html           # Master Layout (Header/Footer/Tailwind)
│   └── home.html           # Homepage Content
│
├── docs/                   # Documentation (You are here)
├── venv/                   # Python Virtual Environment (Do not touch)
├── manage.py               # Django Command Utility
├── db.sqlite3              # The Database File
├── run_portal.bat          # Server Launcher Script
└── dev_shell.bat           # Developer Terminal Script


7. Troubleshooting

Issue: "Script is disabled on this system" error.

Fix: Run this in PowerShell: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Issue: Icons look giant / Colors are missing.

Fix: The Tailwind CDN script isn't loading. Ensure templates/base.html contains the <script src="https://cdn.tailwindcss.com"></script> line and you have an active internet connection.

Issue: "Port already in use".

Fix: You have another server running. Close the other black command window or press Ctrl+C in the active one.