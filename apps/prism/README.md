# Owner Portal (React)

Read-only web app for the technical owner. Shows health, tests, tech debt, and architecture checkpoints from `synapse_analytics.owner.*`.

## Stack
- React 19 + TypeScript + Vite
- TailwindCSS
- React Query + React Router
- Axios (API client)

## Develop
```bash
cd apps/portal
npm install
npm run dev    # http://localhost:4173
```

## Build
```bash
npm run build
npm run preview
```

## Configuration (to wire to real data)
- API base URL: set in `src/shared/config/env.ts` (defaults to `http://localhost:8001`).
- External links (Allure, ReportPortal, Grafana, etc.): `src/shared/config/links.ts`.
- Env file option: copy `.env.example` → `.env` and set `VITE_OWNER_API_BASE_URL` (dev or prod).

## Integration (next steps)
1) Expose FastAPI read-only endpoints (owner_portal) that read `synapse_analytics.owner.*`.
2) Update `src/shared/api/client.ts` baseURL to match your backend routing (Traefik or localhost).
3) Replace mock fetchers in `src/shared/api/hooks.ts` with real HTTP calls.
4) Add Traefik labels / compose service to serve the built app at `portal.localhost`.
