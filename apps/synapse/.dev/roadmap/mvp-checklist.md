# SYNAPSE MVP - Demo Checklist

> Target: December 20, 2025
> Audience: Internal (Boss/Direction)

---

## Demo Scenario

```
┌─────────────────────────────────────────────────────────────────┐
│                    5-MINUTE DEMO FLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. IMPORT (1 min)                                               │
│     → Load 100 instruments from CSV                              │
│     → Show validation feedback                                   │
│     → Show real-time progress in DevConsole                      │
│                                                                  │
│  2. RULES (2 min)                                                │
│     → Execute "Create Motors for Pumps"                          │
│     → Show 49 motors auto-created                                │
│     → Execute "Generate Power Cables"                            │
│     → Show 95 cables with auto-sizing                            │
│     → Show audit trail in DevConsole                             │
│                                                                  │
│  3. TRACEABILITY (1 min)                                         │
│     → Open asset history                                         │
│     → Show diff between versions                                 │
│     → Demonstrate rollback capability                            │
│                                                                  │
│  4. EXPORT (1 min)                                               │
│     → Select Area 210                                            │
│     → Generate IN-P040 (Instrument Index)                        │
│     → Generate CA-P040 (Cable Schedule)                          │
│     → Show professional Excel formatting                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Checklist

### Import

- [ ] CSV import works with 100+ instruments
- [ ] Validation errors displayed clearly
- [ ] Column auto-mapping works
- [ ] Progress shown in DevConsole
- [ ] Import completes in <5 seconds

### Rule Engine

- [ ] CREATE_CHILD rule works (Pump → Motor)
- [ ] CREATE_CABLE rule works with sizing
- [ ] CREATE_PACKAGE rule works
- [ ] Rules execute in batch efficiently
- [ ] Each action logged in DevConsole

### Traceability

- [ ] Asset history shows all changes
- [ ] Diff view shows before/after
- [ ] Rollback works correctly
- [ ] Timeline view available
- [ ] "Who changed what when" answerable

### Export

- [ ] IN-P040 template generates correctly
- [ ] CA-P040 template generates correctly
- [ ] Excel formatting is professional
- [ ] Headers/footers correct
- [ ] Data is accurate

### UI/UX

- [ ] VSCode-like interface loads cleanly
- [ ] Panels resize correctly
- [ ] Navigation is intuitive
- [ ] DevConsole shows real-time logs
- [ ] No obvious bugs/glitches

### Data

- [ ] Demo dataset loaded (seed_demo)
- [ ] 2 clients, 2 projects configured
- [ ] Sample rules configured
- [ ] WBS packages ready

---

## Pre-Demo Checklist

```bash
# 1. Start infrastructure
cd forge && docker compose up -d

# 2. Start SYNAPSE
cd apps/synapse && docker compose -f docker-compose.dev.yml up -d

# 3. Seed demo data
cd apps/synapse/backend
python -m app.scripts.seed_demo

# 4. Verify services
curl http://localhost:4000/api/v1/health

# 5. Open browser
open http://localhost:4000
```

---

## Talking Points

| Question | Answer |
|:---------|:-------|
| "Why not use AWS tool?" | Self-hosted, more flexible, we control the roadmap |
| "Is it production ready?" | MVP for demo, needs tests & polish for production |
| "How long to build?" | ~4 weeks intensive development |
| "Who can maintain it?" | Internal team, standard tech stack |
| "What's next?" | Plant 3D integration, more templates, NEXUS portal |

---

## Backup Plan

If something fails during demo:

1. **Import fails**: Use pre-loaded data, skip import step
2. **Rules fail**: Show rule configuration, explain logic
3. **Export fails**: Show template files, explain generation
4. **UI crashes**: Use API docs (Swagger) to show endpoints

---

*Last updated: 2025-11-30*
