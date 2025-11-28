# Changelog

All notable changes to SYNAPSE will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Bootstrap system for easy setup (`scripts/bootstrap.ps1`, `scripts/bootstrap.sh`)
- Database seeding script with demo data (`backend/app/scripts/seed_all.py`)
- Sample P&ID import file (`backend/data/sample_pid_import.csv`)
- AI-first documentation structure (`AI_START.md`, `GEMINI.md`)
- WSL2 optimization script (`scripts/optimize_wsl.ps1`)
- Environment template (`.env.example`)
- Versioning documentation (`docs/00_OVERVIEW/10_VERSIONING.md`)

### Changed
- Restructured AI documentation for Claude Code and Antigravity compatibility
- Updated `CLAUDE.md` with current project structure
- Cleaned up obsolete files at project root

### Fixed
- Removed outdated documentation files

---

## [0.2.0-dev] - 2025-11-23

### Added
- **Phase 1: Multi-Project Structure**
  - Clients & Projects tables
  - Project selector UI
  - Data filtered by selected project

- **Phase 2: Data Completion & Validation**
  - Enhanced rule engine (6 action types)
  - Rule priority system (CLIENT > PROJECT > COUNTRY > FIRM)
  - 14 baseline rules seeded
  - Data validation & warnings

- **Phase 5: Enhanced UI** (95% complete)
  - Hierarchical navigation menu
  - Dark/Light theme toggle
  - AG Grid Theming API integration
  - Column management & presets
  - Filter presets
  - Keyboard shortcuts

### In Progress
- Cross-browser testing (Firefox, Edge)

---

## [0.1.0] - 2025-11-01

### Added
- Initial prototype
- Basic asset management
- Simple rule execution
- PostgreSQL database setup
- React frontend with AG Grid
- FastAPI backend

---

## Version History Summary

| Version | Date | Status |
|---------|------|--------|
| 0.2.0-dev | 2025-11-23 | In Development |
| 0.1.0 | 2025-11-01 | Released |
