# Testing Infrastructure - Quick Decision Guide

**Primary reporting: local HTML + Vitest UI**

---

## 🧪 Backend (pytest + HTML)

**Quick Start**
```bash
cd apps/synapse/backend
pytest --html=reports/backend-report.html --self-contained-html
```

- Rapport: `apps/synapse/backend/reports/backend-report.html`
- Plugin: `pytest-html` (déclaré dans `requirements.txt`)

---

## 🎭 Frontend E2E (Playwright + HTML)

**Quick Start**
```bash
cd apps/synapse/frontend
npx playwright test
```

- Rapport HTML: généré par le reporter Playwright par défaut (`playwright-report/`).

---

## ⚛️ Portal (React) - Vitest UI

**Quick Start**
```bash
cd apps/portal
npm run test:ui
```

- Ouvre automatiquement l’UI Vitest (par défaut sur `http://localhost:5130`).

---

## 📁 Files Structure (tests)

```
apps/
├── synapse/
│   ├── backend/            # pytest + pytest-html
│   └── frontend/           # Playwright E2E + HTML report
└── portal/                 # Vitest + Vitest UI
```

---

**Updated:** 2025-11-26
