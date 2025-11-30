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

### Contexte "Self-Perform"

La firme exécute l'ensemble du cycle de projet en interne, sans sous-traitance majeure. Cela implique:

- Contrôle total sur la qualité
- Besoin accru de traçabilité
- Gestion d'un grand volume d'assets (instruments, câbles, équipements)
- Coordination multi-disciplinaire intensive
- Documentation rigoureuse pour conformité minière

---

## Pourquoi AXIOM?

### Pain Points Identifiés (à compléter)

| Problème | Impact | Solution AXIOM |
|:---------|:-------|:---------------|
| Gestion manuelle des instruments | Temps, erreurs | SYNAPSE - Import CSV automatisé |
| Création de câbles électriques | Calculs répétitifs | Rule Engine - CREATE_CABLE |
| Génération de livrables | Formatage manuel Excel | Templates IN-P040, CA-P040 |
| Traçabilité des changements | Audits difficiles | Workflow Logger + Versioning |
| *À documenter...* | | |

### Vision

AXIOM = Plateforme unifiée qui:
1. **Automatise** les tâches répétitives d'ingénierie
2. **Trace** chaque action pour les audits
3. **Génère** les livrables standards automatiquement
4. **Centralise** les connaissances (NEXUS)
5. **Augmente** la productivité avec l'AI (ATLAS)

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

### NEXUS - Knowledge Portal (Usage Mixte)

*À documenter: usage prévu*

### Usage Personnel

*À documenter: outils souhaités*

---

## Roadmap & Objectifs

### Court Terme - MVP Demo (20 décembre 2025)

**Objectif:** Démontrer la valeur de SYNAPSE à [audience à préciser]

**Scénario de démo probable:**
1. Importer une liste d'instruments (ex: 100 instruments d'une zone de procédé)
2. Exécuter les règles automatiques (création moteurs, câbles)
3. Montrer la traçabilité en temps réel
4. Exporter un package livrable (IN-P040)

### Moyen Terme

*À documenter*

### Long Terme

*À documenter*

---

## Notes de Conversation

### 2025-11-30 - Session Initiale

**Contexte établi:**
- Ingénieur automatisation, mines d'or, Québec
- Firme EPCM self-perform (faisabilité → construction)
- AXIOM = outil professionnel + personnel

**Questions en attente:**
- [ ] Détails sur les pain points quotidiens
- [ ] Public cible de la démo du 20 décembre
- [ ] Usage prévu de NEXUS
- [ ] Fonctionnalités personnelles souhaitées

---

*Document maintenu par ATLAS pour contexte AI*
