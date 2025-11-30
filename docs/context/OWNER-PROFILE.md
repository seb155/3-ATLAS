# AXIOM - Owner Profile & Project Context

> **Document vivant** - Mis à jour au fil des conversations
>
> Dernière mise à jour: 2025-11-30

---

## Owner Profile

### Identité Professionnelle

| Aspect | Détail |
|:-------|:-------|
| **Rôle** | Ingénieur en automatisation |
| **Industrie** | Mines d'or (Gold Mining) |
| **Localisation** | Québec, Canada |
| **Type de firme** | Firme de génie EPCM complète |
| **Modèle d'affaires** | Self-perform (faisabilité → construction) |

### Expertise Technique

- Automatisation industrielle
- Instrumentation & contrôle
- Projets miniers (extraction aurifère)
- Cycle complet EPCM:
  - **E**ngineering (Études de faisabilité, ingénierie détaillée)
  - **P**rocurement (Approvisionnement équipements)
  - **C**onstruction (Exécution terrain)
  - **M**anagement (Gestion de projet intégrée)

### Contexte "Self-Perform" & Fast-Track

La firme exécute l'ensemble du cycle de projet en interne, en mode **fast-track**:

**Philosophie "Juste assez":**
- Ingénierie suffisante pour obtenir les permis
- Fixer le prix du projet
- Passer les commandes d'équipements
- Démarrer la construction

**Concurrent Engineering:**
- L'ingénierie de détail se termine **en même temps** que la construction
- Pas de phase séquentielle traditionnelle
- Flexibilité maximale, adaptation en temps réel

**Implications:**
- Besoin d'outils agiles qui suivent le rythme
- Traçabilité critique (qui a changé quoi, quand, pourquoi)
- Génération rapide de livrables
- Intégration avec les données terrain (Plant 3D)

---

## Propriété Intellectuelle & Modèle Business

### Statut IP

| Aspect | Détail |
|:-------|:-------|
| **Propriétaire** | Owner (développeur individuel) |
| **Repository** | Privé (GitHub) |
| **Licence actuelle** | Propriétaire |

### Stratégie de Monétisation

**AXIOM reste la propriété du développeur.** Options envisagées avec l'employeur:

#### Option 1: Vente de Parts
- L'employeur acquiert des parts dans le projet
- Participation au développement et tests
- Partage des bénéfices futurs

#### Option 2: Licence Avantageuse
- Licence d'utilisation pour l'employeur
- Tarification préférentielle (early adopter)
- L'employeur aide au développement/testing
- Owner conserve 100% de la propriété

#### Option 3: Modèle Hybride
- Licence + participation au développement
- Co-développement de features spécifiques
- Owner garde le contrôle de la roadmap

### Avantages pour l'Employeur

| Avantage | Description |
|:---------|:------------|
| **Coût réduit** | Pas de développement from scratch |
| **Influence** | Participer à façonner l'outil |
| **Support** | Développeur interne dédié |
| **Flexibilité** | Customisation possible |
| **Self-hosted** | Données on-premise, pas de cloud |

### Protection IP

- Code source privé
- Documentation technique protégée
- Démo = proof of concept, pas le code complet
- NDA si discussion approfondie

---

## Environnement Existant (Chez l'Employeur)

### Outils Actuels

La firme a déjà développé des outils internes:

#### 1. Outils Excel + Plant 3D
Fichiers Excel qui lisent les données P&ID de **AutoCAD Plant 3D** et génèrent:
- Liste de I/O (Input/Output)
- Liste de câbles
- Liste d'instruments
- Dessins électriques (panneaux PLC et RIO)

#### 2. Outil AWS (Cloud)
Application web sur AWS qui:
- Lit la database SQL de Plant 3D
- Utilise des **Lambda rules** pour générer des éléments de base
- Affiche les données dans **AG-Grid** (vue "à plat")
- Permet de modifier certaines valeurs non verrouillées par Plant 3D

**Limitations actuelles:**
- Pas de résultat concret/abouti
- Vue tabulaire simple sans hiérarchie
- Cloud = dépendance externe, coûts récurrents
- Flexibilité limitée pour développement interne

---

## Pourquoi AXIOM?

### Positionnement vs Outils Existants

| Aspect | Outils Actuels | AXIOM |
|:-------|:---------------|:------|
| **Hébergement** | AWS Cloud | Self-hosted (contrôle total) |
| **Flexibilité** | Lambda rules figées | Rule Engine configurable |
| **UI/UX** | AG-Grid basique | Interface VSCode-like moderne |
| **Traçabilité** | Limitée | Event sourcing complet |
| **Évolutivité** | Dépend d'AWS | Développement interne libre |
| **Coûts** | Récurrents (cloud) | Infrastructure maîtrisée |

### Argument Clé pour la Démo

> **"Self-hosted, plus performant, plus flexible pour le développement interne"**

AXIOM démontre qu'une solution maison peut:
1. Égaler (et dépasser) les capacités des outils cloud
2. Offrir un contrôle total sur l'évolution
3. S'adapter au mode fast-track de la firme
4. Être développée et maintenue à l'interne

### Vision

AXIOM = Plateforme unifiée qui:
1. **Automatise** les tâches répétitives d'ingénierie
2. **Trace** chaque action pour les audits
3. **Génère** les livrables standards automatiquement
4. **Centralise** les connaissances (NEXUS)
5. **Augmente** la productivité avec l'AI (ATLAS)
6. **Libère** la firme des dépendances cloud externes

---

## Applications & Usage

### SYNAPSE - Plateforme MBSE (Usage Professionnel)

**Cas d'usage mines d'or:**

| Fonctionnalité | Application Minière |
|:---------------|:--------------------|
| Import CSV | Importer liste d'instruments depuis études faisabilité |
| Rule Engine | Auto-générer moteurs pour pompes de procédé |
| CREATE_CABLE | Calculer et créer câbles avec sizing automatique |
| CREATE_PACKAGE | Grouper équipements par zone/WBS |
| Templates Export | Générer Instrument Index (IN-P040) pour soumissions |

**Équipements typiques gérés:**
- Pompes de procédé (slurry, eau de procédé)
- Moteurs électriques
- Instrumentation (transmetteurs, vannes, analyseurs)
- Câblage électrique et instrumentation
- Équipements de broyage/concassage
- Systèmes de contrôle

**Intégration Plant 3D (Future):**
- Lecture directe de la database SQL Plant 3D
- Synchronisation bidirectionnelle des données
- Remplacement des outils Excel existants

---

### NEXUS - Portail Employé (Usage Professionnel)

**Vision:** Portail unifié où l'employé trouve **tout ce dont il a besoin**.

#### Fonctionnalités Prévues

| Module | Description |
|:-------|:------------|
| **Contexte Personnel** | Profil, préférences, settings pour l'AI |
| **Gestion des Tâches** | Tasks de travail assignées |
| **Tâches AI** | Tasks déléguées aux agents AI, suivi d'exécution |
| **Notes & Wiki** | Notes personnelles, documentation, wiki collaboratif |
| **Documentation Technique** | Accès à la doc (actuellement M-Files & SharePoint) |
| **Outils de Schémas** | Dessins rapides, annotations, diagrammes |
| **Productivité** | Dashboards personnels, métriques |

#### Sources de Données Externes

| Source | Type | Intégration |
|:-------|:-----|:------------|
| **M-Files** | GED (Gestion Électronique Documents) | Lecture/indexation |
| **SharePoint** | Documentation corporate | Lecture/indexation |
| **Plant 3D** | Données P&ID | Via SYNAPSE |

---

### CORTEX - Memory Engine (Dans ATLAS)

**Rôle:** Mémoire persistante pour les agents AI

- **HOT:** Contexte de session actif
- **WARM:** Projets récents, patterns fréquents
- **COLD:** Archives, historique complet

Permet aux AI de "se souvenir" du contexte projet, des décisions passées, et d'apprendre des patterns.

---

### Usage Personnel (Instance Séparée)

**Concept:** Déployer une instance AXIOM personnelle chez soi.

#### Vision

```
┌─────────────────────────────────────────────────────────┐
│              AXIOM Personnel (Home Instance)            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   NEXUS     │  │   CORTEX    │  │  FinDash    │    │
│  │  Personnel  │  │  (AI Memory)│  │  (Finances) │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                         │
│  Features:                                              │
│  • Profil personnel (pour AI)                          │
│  • Notes & wiki personnel                              │
│  • Productivité & habits                               │
│  • Gestion finances (FinDash)                          │
│  • AI assistant personnel (CORTEX)                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### Séparation des Instances

| Instance | Hébergement | Usage |
|:---------|:------------|:------|
| **AXIOM Pro** | Serveur firme | Travail, projets miniers |
| **AXIOM Perso** | Home server | Vie personnelle, finances |
| **CORTEX** | Partagé ou séparé | AI memory (peut être commun) |

#### Synergie

- Même plateforme, deux contextes
- AI peut apprendre des deux (si voulu)
- Skills transférables (productivité → travail)

---

## Roadmap & Objectifs

### Court Terme - MVP Demo (20 décembre 2025)

**Audience:** Boss / Direction interne
**Objectif:** Démontrer que AXIOM est une alternative viable et supérieure aux outils existants

#### Message Clé de la Démo

> "Voici ce que je suis capable de faire. C'est self-hosted, plus performant,
> et plus flexible pour qu'on développe à l'interne."

#### Scénario de Démo - Workflow Complet

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DÉMO WORKFLOW END-TO-END                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. IMPORT                    2. RULES                    3. EXPORT        │
│  ┌─────────────────┐         ┌─────────────────┐         ┌──────────────┐  │
│  │  Plant 3D SQL   │────────▶│  Rule Engine    │────────▶│ Excel Pro    │  │
│  │  (POC)          │         │  Auto-generate  │         │ IN-P040      │  │
│  │                 │         │                 │         │ CA-P040      │  │
│  │  CSV/Excel      │         │  • Motors       │         │ IO-List      │  │
│  │  (Backup)       │         │  • Cables       │         │              │  │
│  └─────────────────┘         │  • Packages     │         └──────────────┘  │
│         │                    └────────┬────────┘                │          │
│         │                             │                         │          │
│         ▼                             ▼                         ▼          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        FEATURES TRANSVERSES                          │   │
│  │  • Traçabilité complète (qui/quoi/quand/pourquoi)                   │   │
│  │  • Historique de versions (diff, rollback)                          │   │
│  │  • Structures: FBS / LBS / CBS / WBS                                │   │
│  │  • Logs temps réel (DevConsole)                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 1. Import - Proof of Concept

| Source | Status | Description |
|:-------|:-------|:------------|
| **Plant 3D SQL** | POC | Lecture directe de la DB SQL (démo principale) |
| **CSV/Excel** | Ready | Import manuel (backup, autres sources) |
| **Autres logiciels** | Future | Architecture extensible pour d'autres sources |

**Architecture d'import extensible:**
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Plant 3D      │     │   CSV/Excel     │     │   Future        │
│   Connector     │     │   Connector     │     │   Connectors    │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Import Service        │
                    │   (Unified Interface)   │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Asset Database        │
                    └─────────────────────────┘
```

#### 2. Rules - Automatisation

| Rule | Action | Exemple |
|:-----|:-------|:--------|
| **CREATE_CHILD** | Crée asset enfant | Pompe → Moteur automatique |
| **CREATE_CABLE** | Crée câble + sizing | Motor → Cable avec calcul AWG |
| **CREATE_PACKAGE** | Groupe en package | Zone 210 → Package IN-P040 |

#### 3. Export - Livrables Professionnels

| Template | Description | Format |
|:---------|:------------|:-------|
| **IN-P040** | Instrument Index | Excel formaté |
| **CA-P040** | Cable Schedule | Excel formaté |
| **IO-List** | Liste I/O | Excel formaté |

**Qualité attendue:** Format professionnel, prêt pour soumission client.

#### 4. Features Transverses

| Feature | Description |
|:--------|:------------|
| **Traçabilité** | Event sourcing - chaque action loggée |
| **Versions** | Historique complet, diff entre versions, rollback |
| **Structures** | FBS (Functional), LBS (Location), CBS (Cost), WBS (Work) |
| **DevConsole** | Logs temps réel pendant les opérations |
| **Search** | Full-text search (MeiliSearch) |

#### Différenciateurs à Mettre en Avant

| Aspect | Outil AWS Actuel | AXIOM |
|:-------|:-----------------|:------|
| Résultat | "Rien de concret" | Démo fonctionnelle end-to-end |
| Hébergement | Cloud (dépendance) | Self-hosted (autonomie) |
| UI | AG-Grid plat | VSCode-like, hiérarchique |
| Rules | Lambda (rigide) | Rule Engine configurable |
| Évolution | Limité par AWS | Développement libre |
| Import | SQL read only | Multi-source extensible |
| Export | Basique | Excel professionnel formaté |
| Structures | Flat | FBS/LBS/CBS/WBS hiérarchiques |

### Moyen Terme (Q1 2026)

- **Plant 3D Integration:** Connecter directement à la DB SQL Plant 3D
- **NEXUS Phase 1:** Portail employé basique (tâches, notes)
- **Remplacer Excel:** Migration des outils Excel vers SYNAPSE

### Long Terme (2026+)

- **NEXUS Complet:** M-Files/SharePoint integration, wiki, productivité
- **APEX:** Dashboard enterprise, launcher
- **AI Avancé:** CORTEX mémoire, agents autonomes
- **Instance Personnelle:** Déploiement home server

---

## Notes de Conversation

### 2025-11-30 - Session Initiale

**Contexte établi:**
- Ingénieur automatisation, mines d'or, Québec
- Firme EPCM self-perform (faisabilité → construction)
- Mode fast-track: ingénierie de détail termine en même temps que construction
- AXIOM = outil professionnel + personnel

**Environnement existant documenté:**
- [x] Outils Excel + Plant 3D (listes I/O, câbles, instruments, dessins PLC/RIO)
- [x] Outil AWS (Lambda rules, AG-Grid, lecture SQL Plant 3D)
- [x] Limitations: pas de résultat concret, vue plate, dépendance cloud

**Démo 20 décembre:**
- [x] Audience: Boss / direction interne
- [x] Objectif: Montrer capacités + argument self-hosted vs cloud
- [x] Message: "Plus performant, plus flexible, développement interne"

**NEXUS clarifié:**
- [x] Portail employé complet
- [x] Gestion contexte, tâches travail, tâches AI
- [x] Notes/wiki personnel
- [x] Accès doc technique (M-Files, SharePoint)
- [x] Outils schémas/annotations

**Usage personnel clarifié:**
- [x] Instance séparée déployée à domicile
- [x] Reliée à outils finances (FinDash)
- [x] Accès CORTEX et AI
- [x] Même concept que portail employé pour vie personnelle

---

## Idées & Insights

### Opportunités Identifiées

1. **Plant 3D comme source unique**
   - Connecter SYNAPSE directement à la DB SQL
   - Éliminer les Excel intermédiaires
   - Sync bidirectionnelle

2. **Rule Engine > Lambda**
   - Règles configurables sans redeploy
   - UI pour créer/modifier les règles
   - Historique d'exécution complet

3. **Portail Employé Unifié (NEXUS)**
   - Single point of entry
   - Réduire friction M-Files/SharePoint
   - AI-augmented productivity

4. **Self-hosted = Argument Fort**
   - Pas de vendor lock-in AWS
   - Coûts prévisibles
   - Données sensibles on-premise
   - Développement libre

---

*Document maintenu par ATLAS pour contexte AI*
