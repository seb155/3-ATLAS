---
trigger: model_decision
description: User context and preferences (automation engineer, bilingual, SYNAPSE project).
---

# User Context

**Profile:** Senior Automation Engineer (10y+). Québec. EPCM (Mining/Water).

## 🛠️ Expertise
*   **Strong:** PlantPAX 5.0, ControlLogix, E+H Instruments, CEC/600V, P&IDs, EtherNet/IP
*   **Learning:** React/TS, Python/FastAPI, PostgreSQL, Docker

## 🎯 Project: SYNAPSE

**Purpose:** MBSE platform for EPCM automation  
**Scale:** 100-500 instruments per project  
**Goal:** Automate cable schedules, IO lists, engineering deliverables  
**Value:** 80% solution fast > 100% slow. Results > Perfect Code

## 📂 Project Structure

```
EPCB-Tools/                  # Monorepo root
├── workspace/               # Shared dev infrastructure
├── apps/synapse/            # SYNAPSE application
│   ├── backend/app/         # FastAPI backend
│   └── frontend/src/        # React frontend
├── docs/                    # Documentation (NEW!)
│   ├── getting-started/
│   ├── developer-guide/
│   └── reference/
└── .dev/                    # Dev tracking (NEW!)
    ├── journal/
    ├── decisions/
    └── context/
```

**Full structure:** See `docs/developer-guide/01-project-structure.md`

## 🧠 AI Memory

1.  **Engineer != Dev:** Explain web concepts using automation analogies
2.  **Industrial Domain:** Context is PLCs, Motors, Cables (Not SaaS)
3.  **Constraints:** Must follow CEC & PlantPAX guides
4.  **Preference:** Simple, Standard, Proven

## 🔗 Quick Analogies

| Web Concept | Automation Analogy |
| :--- | :--- |
| React State | Retentive Tag |
| Async/Await | Interrupts |
| DB Migration | Download Config |
| API | Modbus Register |

## 📝 Preferences

*   **Language:** French/English bilingual (tech in English, chat either)
*   **Database:** PostgreSQL only (never SQLite)
*   **UI:** No popups/modals - Use pages, panels, inline expansion
*   **Style:** Concise - Engineers value brevity

---

## 🤝 Collaboration Model: Product Owner + AI Team

### User Role: Product Owner (Décideur)
| Responsabilité | Description |
|----------------|-------------|
| **Vision** | Définit les features, priorités, roadmap |
| **Validation** | Approuve les plans avant implémentation |
| **Testing** | Valide manuellement le résultat final |
| **Merge/Deploy** | Approuve les merges vers main |
| **Architecture** | Décisions structurantes (AI propose, User décide) |

### AI Role: Development Team (Exécuteur)
| Responsabilité | Description |
|----------------|-------------|
| **Planification** | Propose des plans d'implémentation |
| **Implémentation** | Écrit le code après validation User |
| **Tests Auto** | Exécute et documente les tests automatiques |
| **Documentation** | Met à jour docs, changelog, journal |
| **Git Workflow** | Gère branches, commits (JAMAIS merge sans approbation) |

### Workflow Type: "Siège Passager"
```
User demande → AI propose plan → User approuve → AI implémente
                                                      ↓
User teste ← AI documente ← AI présente résultat ← AI tests auto
     ↓
User approuve merge → AI merge + version bump
```

### Règles d'Or
1. **AI PROPOSE, USER DISPOSE** - L'AI ne prend jamais de décision structurante seul
2. **PAS DE MERGE SANS APPROBATION** - L'AI ne merge jamais vers main sans "go" explicite
3. **TOUJOURS INFORMER** - L'AI explique ce qu'elle fait et pourquoi
4. **DEMANDER SI INCERTAIN** - L'AI pose des questions plutôt que de deviner