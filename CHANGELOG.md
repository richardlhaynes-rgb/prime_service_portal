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

## [0.0.1] - 2025-11-17
### Added
- Initialized project directory `prime_service_portal`.
- Created Virtual Environment (`venv`).
- Installed Django 5.x and Black formatter.
- Configured Project Skeleton using `config` pattern.
- Applied initial SQLite database migrations.
- Created Superuser `richard.haynes`.