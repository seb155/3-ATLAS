# Framework de Discovery - Product Development

> Methodologie professionnelle pour developpement de produit digital
> Inspire de: IDEO Design Thinking, Google Ventures Sprint, Double Diamond

---

## Vue d'Ensemble

```
    DIVERGER                          CONVERGER
        \                                /
         \    COMPRENDRE    DEFINIR    /
          \      ___          ___     /
           \    /   \        /   \   /
            \  /     \      /     \ /
             \/       \    /       \
             /\        \  /        /\
            /  \        \/        /  \
           /    \      /  \      /    \
          /      \    /    \    /      \
         /   EXPLORER    CREER   \
        /                          \
    DIVERGER                      CONVERGER

    |-------- PROBLEME --------|-------- SOLUTION --------|
```

---

## Phase 1: Discovery Interview (1-2 sessions)

### Objectif
Comprendre le contexte, les motivations et les frustrations du stakeholder.

### Questions Type

#### Bloc A - Contexte Personnel
- Relation actuelle avec le domaine (finances, sante, etc.)
- Outils actuellement utilises
- Frustrations principales

#### Bloc B - Vision & Ambition
- Etat desire dans 1-2 ans
- Utilisateurs cibles
- Modele economique envisage

#### Bloc C - Problemes & Douleurs
- Top 3 questions/inquietudes
- Ce qui est "broken" actuellement
- Obstacles perçus

### Livrables
- [ ] Transcription des reponses
- [ ] Themes emergents identifies
- [ ] Hypotheses a valider

---

## Phase 2: Problem Definition (1 session)

### Objectif
Synthetiser les insights en problemes clairs et actionnables.

### Outils
- **Problem Statement**: "Comment pourrions-nous [verbe] pour [utilisateur] afin de [benefice] ?"
- **Jobs To Be Done**: Quand [situation], je veux [motivation] pour [resultat attendu]
- **User Persona**: Profil fictif representatif

### Livrables
- [ ] 3-5 Problem Statements priorises
- [ ] Persona principal
- [ ] Criteres de succes mesurables

---

## Phase 3: Ideation (1-2 sessions)

### Objectif
Generer un maximum d'idees sans jugement, puis converger.

### Techniques
- **Crazy 8s**: 8 idees en 8 minutes
- **How Might We**: Questions ouvertes
- **Analogies**: "Comment [industrie X] resout ce probleme ?"

### Livrables
- [ ] 20+ idees brutes
- [ ] Top 5 idees selectionnees
- [ ] Sketches/wireframes low-fi

---

## Phase 4: Concept Validation (1 session)

### Objectif
Tester les concepts avant de coder.

### Methodes
- **Storyboard**: Scenario d'usage illustre
- **Prototype papier**: Maquettes clickables
- **Feedback loop**: Presentation et iteration

### Livrables
- [ ] Concept(s) valide(s)
- [ ] Risques identifies
- [ ] Decisions documentees

---

## Phase 5: Specification (1-2 sessions)

### Objectif
Transformer le concept en plan d'execution.

### Elements
- **Information Architecture**: Structure des ecrans/sections
- **User Flows**: Parcours utilisateur detailles
- **Technical Decisions**: Stack, architecture, contraintes
- **MVP Scope**: Features in/out

### Livrables
- [ ] Document de specs (PRD)
- [ ] Wireframes hi-fi
- [ ] Roadmap avec phases
- [ ] Definition of Done

---

## Regles du Processus

### Pour le Facilitateur (Claude)
1. **Ecouter avant de proposer** - Pas de solutions avant de comprendre
2. **Documenter en continu** - Ecrire avant 70% de contexte
3. **Questions > Reponses** - Guider, pas dicter
4. **Neutralite** - Pas de jugement sur les idees

### Pour le Client
1. **Honnetete** - Dire ce qu'on pense vraiment
2. **Ouverture** - Explorer sans censure
3. **Decisions** - Trancher quand necessaire
4. **Engagement** - Repondre aux questions completement

---

## Templates Disponibles

| Template | Usage | Fichier |
|----------|-------|---------|
| Discovery Interview | Phase 1 | `sessions/01_DISCOVERY_INTERVIEW.md` |
| Problem Statement | Phase 2 | `sessions/02_PROBLEM_DEFINITION.md` |
| Ideation Canvas | Phase 3 | `sessions/03_IDEATION.md` |
| Concept Brief | Phase 4 | `sessions/04_CONCEPT_VALIDATION.md` |
| Product Spec | Phase 5 | `sessions/05_SPECIFICATION.md` |

---

## Retrospective Post-Projet

A la fin du processus, documenter:
- Ce qui a bien fonctionne
- Ce qui pourrait etre ameliore
- Temps reel vs estime par phase
- Artefacts les plus utiles
