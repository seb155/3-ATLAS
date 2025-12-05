---
description: Start new development session - full context load (Mode FULL)
---

# /0-session-start

Démarre une nouvelle session de développement avec chargement complet du contexte.

**Mode:** FULL (Complete context loading)

## Usage

```bash
/0-session-start              # Nouvelle session dans le projet courant
/0-session-start echo         # Nouvelle session sur ECHO
/0-session-start synapse      # Nouvelle session sur SYNAPSE
/0-session-start mechvision   # Nouvelle session sur MechVision
```

## Arguments

- `[project-id]` (optional): Identifiant du projet cible
  - Case-insensitive ("ECHO" = "echo")
  - Résolution via Rule 31 (project-resolution.md)
  - Si non fourni: détecte automatiquement

## Actions

1. **Résolution du projet** (si argument fourni)
   - Scan les `.dev/.dev-manifest.json` du workspace
   - Match le project-id avec les manifests
   - Si trouvé: charge le contexte de ce projet
   - Si non trouvé: affiche les projets disponibles

2. **Vérifie session active**
   - Lit `.dev/1-sessions/active/current-session.md`
   - Si existe: propose continuer, archiver, ou ignorer
   - Vérifie `.dev/0-backlog/` pour items urgents

3. **Detecte le contexte d'execution**

   **MODE A: Contexte PROJECT** (dans un sous-dossier de projet)
   - Lit `.dev/context/project-state.md`
   - Lit `.dev/context/hot-context.md`
   - Lit le journal recent
   - Verifie l'etat des tests
   - Charge CLAUDE.md du projet

   **MODE B: Contexte ROOT** (dans le workspace root)
   - Lit `.registry/projects.json`
   - Execute scan-projects.ps1 pour collecter le status
   - Affiche Projects Status Table
   - Propose navigation vers un projet specifique

4. **Detecte l'environnement**
   - OS: Windows / Linux
   - Mode: dev / prod
   - Docker: services running

5. **Propose les priorites**
   - Taches en cours, Sprint actuel, Blockers

## Exemple (avec projet spécifié)

```text
User: /0-session-start synapse

ATLAS: "📂 Projet ciblé: SYNAPSE (MBSE Platform)
Path: /home/seb/projects/AXIOM/apps/synapse

Bonjour! Je charge le contexte...

**Environnement**
- OS: Linux (WSL)
- Docker: forge-postgres, forge-redis (healthy)
- Mode: Development

**Application**: SYNAPSE

**Sprint**: MVP Week 3 (Dec 20 deadline)

**Etat des tests**
- Backend: 78% coverage
- Frontend: 72% coverage

**En cours**
- Systeme de notifications (90%)

**Priorites suggeres**
1. Finir tests notifications
2. Integration NEXUS
3. UI polish

**Que veux-tu faire?**
1. Continuer priorité #1 (Tests notifications)
2. Démarrer priorité #2 (Integration NEXUS)
3. Autre tâche (précise)
4. Voir roadmap complet (/0-view-roadmap)"
```

## Agent invoqué

- ATLAS (orchestrateur principal)
- DEV-TRACKER (chargement contexte)
- PROJECTS-SCANNER (MODE ROOT - scan multi-projets)

---

**Tip:** Type `/0-session-start [project]` pour démarrer sur un projet spécifique!

## See Also

- `/0-session-continue` - Continue existing session
- `/0-session-recover` - Recover after /compact
- `/0-view-projects` - View all projects status
- Rule 31 - Project ID resolution
