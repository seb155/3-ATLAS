# Skill: Brainstorm Mode

Active le mode brainstorm/whiteboard pour exploration d'idées.

## Instructions

Quand ce skill est invoqué, activer le mode brainstorm:

### 1. Annoncer le mode

```
🧠 Mode Brainstorm Activé
═══════════════════════════════════════════════════════════════════

Bienvenue dans l'espace de réflexion!

Dans ce mode:
  ✓ Discussion libre et exploration d'idées
  ✓ Diagrammes et visualisations
  ✓ Questions ouvertes et exploration
  ✓ Documentation des décisions

  ✗ Pas de code
  ✗ Pas de modifications de fichiers (sauf docs)
  ✗ Pas d'implémentation

═══════════════════════════════════════════════════════════════════

Qu'est-ce qu'on explore aujourd'hui?
```

### 2. Comportement en mode brainstorm

- **Poser des questions** avant de proposer des solutions
- **Utiliser des diagrammes** ASCII pour visualiser
- **Explorer les alternatives** systématiquement
- **Documenter** les décisions importantes

### 3. Outils disponibles

**Diagramme de flux:**
```
┌─────────┐      ┌─────────┐      ┌─────────┐
│  Start  │ ───▶ │ Process │ ───▶ │   End   │
└─────────┘      └─────────┘      └─────────┘
```

**Pour/Contre:**
```
Option A                    Option B
─────────────────────      ─────────────────────
✓ Avantage 1               ✓ Avantage 1
✓ Avantage 2               ✓ Avantage 2
✗ Inconvénient 1           ✗ Inconvénient 1
```

**Architecture:**
```
┌─────────────────────────────────────────────────┐
│                   System                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Module A │──│ Module B │──│ Module C │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
```

**Timeline:**
```
Phase 1          Phase 2          Phase 3
─────────        ─────────        ─────────
• Task 1         • Task 4         • Task 7
• Task 2         • Task 5         • Task 8
• Task 3         • Task 6         • Task 9
```

### 4. Sortie du mode

Pour sortir du mode brainstorm et passer à l'implémentation:
- Dire "OK on implémente" ou "Prêt à coder"
- Le mode reviendra à DEVELOPMENT

### 5. Documentation

Les idées importantes peuvent être sauvegardées dans:
- `.dev/whiteboard/` - Sessions de brainstorm
- `.dev/decisions/` - Décisions architecturales
- `.dev/design/` - Documents de design

## Notes

- Ce skill active un MODE de conversation, pas un agent
- L'agent Brainstorm (`.claude/agents/brainstorm.md`) contient plus de détails
- Les outputs sont principalement de la documentation, pas du code
