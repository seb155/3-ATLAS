# Workshop Skill - Quick Actions

Ce skill permet de demarrer, reprendre ou verifier le status d'un workshop Design Thinking rapidement.

---

## Usage

**Invoke with**:
- Skill tool: `skill: "0_workshop"`
- Slash command: `/workshop [action] [projet]`
- Directement: "Lance un workshop pour MonApp"

---

## Actions Disponibles

### 1. NEW - Demarrer un Nouveau Workshop

```text
/workshop new [nom-projet]
```

**Ce qui se passe:**
1. Cree le dossier `workshop-[nom-projet]/`
2. Genere tous les fichiers de structure
3. Prepare les templates de sessions
4. Lance la Phase 1: Discovery Interview

**Exemple:**
```text
/workshop new pilote-patrimoine
/workshop new gestion-inventaire
/workshop new app-fitness
```

### 2. RESUME - Reprendre un Workshop

```text
/workshop resume [nom-projet]
```

**Ce qui se passe:**
1. Lit `00_SESSION_RECOVERY.md`
2. Identifie la derniere phase completee
3. Charge le contexte necessaire
4. Reprend exactement ou c'etait rendu

### 3. STATUS - Voir la Progression

```text
/workshop status [nom-projet]
```

**Ce qui se passe:**
1. Affiche la progression des 5 phases
2. Liste les livrables produits
3. Montre la prochaine etape

### 4. LIST - Lister les Workshops

```text
/workshop list
```

**Ce qui se passe:**
1. Scanne les dossiers `workshop-*/`
2. Affiche chaque workshop avec son status

---

## Implementation

Quand ce skill est invoque:

### Step 1: Parser la Commande

Detecter l'action demandee:
- `new` → Creer nouveau workshop
- `resume` → Reprendre existant
- `status` → Afficher progression
- `list` → Lister tous les workshops
- (aucune action) → Demander ce que l'utilisateur veut faire

### Step 2: Executer l'Action

#### Pour NEW:

1. **Creer la structure de dossiers:**
```
workshop-[nom-projet]/
├── README.md
├── EXECUTIVE_SUMMARY.md
├── 00_PROCESS_FRAMEWORK.md
├── 00_SESSION_RECOVERY.md
├── sessions/
│   ├── 01_DISCOVERY_INTERVIEW.md
│   ├── 02_PROBLEM_DEFINITION.md
│   ├── 03_IDEATION.md
│   ├── 04_CONCEPT_VALIDATION.md
│   └── 05_SPECIFICATION.md
├── artifacts/
└── decisions/
```

2. **Generer les fichiers depuis templates:**
   - Lire `.claude/templates/workshop/` pour les templates
   - Remplacer `[PROJECT_NAME]` par le nom du projet
   - Ecrire les fichiers

3. **Dispatcher vers WORKSHOP-FACILITATOR:**
   ```
   subagent_type: "workshop-facilitator"
   prompt: "Nouveau workshop pour [nom-projet]. Structure creee. Commence Phase 1: Discovery Interview."
   ```

#### Pour RESUME:

1. **Lire le fichier recovery:**
   ```
   Read: workshop-[nom-projet]/00_SESSION_RECOVERY.md
   ```

2. **Identifier l'etat:**
   - Phase actuelle
   - Derniere etape completee
   - Prochaine action

3. **Dispatcher vers WORKSHOP-FACILITATOR:**
   ```
   subagent_type: "workshop-facilitator"
   prompt: "Reprise workshop [nom-projet]. [Contexte du recovery]. Continue a partir de [phase/etape]."
   ```

#### Pour STATUS:

1. **Lire README.md du workshop:**
   ```
   Read: workshop-[nom-projet]/README.md
   ```

2. **Afficher progression:**
   ```markdown
   # Workshop: [nom-projet]

   ## Progression

   | Phase | Status | Date |
   |-------|--------|------|
   | 1. Discovery Interview | COMPLETE | 2024-11-28 |
   | 2. Problem Definition | COMPLETE | 2024-11-28 |
   | 3. Ideation | IN PROGRESS | - |
   | 4. Concept Validation | PENDING | - |
   | 5. Specification | PENDING | - |

   ## Artifacts Produits
   - artifacts/BILAN_ACTUEL.md
   - artifacts/UI_ANALYSIS.md

   ## Prochaine Etape
   Continuer Phase 3: Ideation - Generer idees avec Crazy 8s

   **Commandes:**
   - `/workshop resume [nom-projet]` - Reprendre
   - `/workshop status [nom-projet]` - Ce status
   ```

#### Pour LIST:

1. **Scanner les dossiers:**
   ```powershell
   Get-ChildItem -Directory -Filter "workshop-*"
   ```

2. **Pour chaque workshop, lire le status**

3. **Afficher:**
   ```markdown
   # Workshops Disponibles

   | Projet | Phase | Status | Derniere Activite |
   |--------|-------|--------|-------------------|
   | pilote-patrimoine | 3/5 | Ideation | 2024-11-28 |
   | app-fitness | 1/5 | Discovery | 2024-11-25 |

   **Commandes:**
   - `/workshop resume [projet]` - Reprendre un workshop
   - `/workshop new [projet]` - Creer nouveau workshop
   ```

---

## Output Format

### Pour NEW

```markdown
# Nouveau Workshop: [nom-projet]

Structure creee dans `workshop-[nom-projet]/`

## Fichiers Generes
- README.md (index)
- 00_PROCESS_FRAMEWORK.md (methodologie)
- 00_SESSION_RECOVERY.md (recovery)
- sessions/ (5 templates de phases)
- artifacts/ (vide)
- decisions/ (vide)

## Demarrage Phase 1

Bienvenue dans le Workshop Design Thinking pour **[nom-projet]**!

Commencons par la Phase 1: Discovery Interview.

**Premiere question:**
Parle-moi de toi et de ta relation avec [domaine du projet].
- Comment geres-tu [probleme] aujourd'hui?
- Quels outils utilises-tu actuellement?
- Qu'est-ce qui te frustre le plus?
```

### Pour RESUME

```markdown
# Reprise Workshop: [nom-projet]

## Etat Retrouve
- **Phase actuelle:** 3 - Ideation
- **Derniere action:** Top 5 idees selectionnees
- **Timestamp:** 2024-11-28 15:30

## Contexte Rapide
[Resume du projet et decisions prises]

## On Continue

On en etait a evaluer les trade-offs des 5 idees selectionnees.

**Prochaine etape:** Creer wireframes low-fi pour top 3 idees

Tu veux continuer ou revoir quelque chose avant?
```

### Pour STATUS

```markdown
# Workshop Status: [nom-projet]

## Progression: 60% (Phase 3/5)

| Phase | Status |
|-------|--------|
| 1. Discovery Interview | COMPLETE |
| 2. Problem Definition | COMPLETE |
| 3. Ideation | IN PROGRESS (60%) |
| 4. Concept Validation | PENDING |
| 5. Specification | PENDING |

## Livrables Produits
- Problem Statements (3)
- Persona principal
- 20+ idees brutes
- Top 5 selectionnees

## Prochaine Etape
Finaliser wireframes low-fi

**Actions:**
1. `/workshop resume [nom-projet]` - Continuer
2. Voir artifacts: `workshop-[nom-projet]/artifacts/`
```

---

## Handoff vers Agent

Pour les sessions interactives (new, resume), ce skill dispatche vers l'agent WORKSHOP-FACILITATOR:

```markdown
## Session Interactive Requise

Ce workshop necessite une session interactive avec le facilitateur.

**Invocation de WORKSHOP-FACILITATOR...**
```

Puis utiliser le Task tool:
```
subagent_type: "workshop-facilitator"
prompt: "[Contexte de la demande]"
model: opus
```

---

## Templates Location

Les templates de workshop sont stockes dans:
```
.claude/templates/workshop/
├── README.template.md
├── EXECUTIVE_SUMMARY.template.md
├── 00_PROCESS_FRAMEWORK.md
├── 00_SESSION_RECOVERY.template.md
└── sessions/
    ├── 01_DISCOVERY_INTERVIEW.template.md
    ├── 02_PROBLEM_DEFINITION.template.md
    ├── 03_IDEATION.template.md
    ├── 04_CONCEPT_VALIDATION.template.md
    └── 05_SPECIFICATION.template.md
```

---

## Quick Reference

| Action | Commande | Resultat |
|--------|----------|----------|
| Nouveau | `/workshop new monapp` | Cree structure + lance Phase 1 |
| Reprendre | `/workshop resume monapp` | Charge contexte + continue |
| Status | `/workshop status monapp` | Affiche progression |
| Lister | `/workshop list` | Liste tous les workshops |

---

**Ce skill est ton point d'entree rapide pour les workshops. Pour les sessions interactives, il dispatche vers WORKSHOP-FACILITATOR (Opus).**
