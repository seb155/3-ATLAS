# ATLAS 2.0 - Guide de Continuation

## Nouvelle Session? Copie-colle ceci:

```
Je continue l'implémentation ATLAS 2.0.

Contexte:
- Plan complet: .atlas/ATLAS-2.0-PLAN.md
- Progression: .atlas/ATLAS-2.0-PROGRESS.md

Lis ces fichiers et reprends à la prochaine phase non complétée.
Update le fichier PROGRESS.md après chaque tâche terminée.
```

---

## Commandes Rapides

```bash
# État actuel
cat .atlas/ATLAS-2.0-PROGRESS.md | head -50

# Phase spécifique
grep -A 20 "Phase 0:" .atlas/ATLAS-2.0-PLAN.md

# Voir symlink actuel
ls -la .claude
```

---

## Phases en Bref

| Phase | Commande pour commencer |
|-------|-------------------------|
| 0 | "Exécute Phase 0: Migration symlinks" |
| 1 | "Exécute Phase 1: Crée les builder agents" |
| 2 | "Exécute Phase 2: Configure git worktrees" |
| 3 | "Exécute Phase 3: Setup sandbox pool dans FORGE" |
| 4 | "Exécute Phase 4: Configure monorepo layers" |
| 5 | "Exécute Phase 5: Setup inter-agent comms" |

---

## Si Erreur / Blocage

1. **Symlink cassé:**
   ```bash
   # Restaurer depuis backup
   cp -r /tmp/atlas-backup/.claude /home/user/AXIOM/.claude
   ```

2. **Worktree corrompu:**
   ```bash
   git worktree prune
   git worktree list
   ```

3. **Sandbox pool down:**
   ```bash
   cd forge/sandbox && docker compose down && docker compose up -d
   ```

---

## Fichiers Clés

| Fichier | Rôle |
|---------|------|
| `.atlas/ATLAS-2.0-PLAN.md` | Plan détaillé avec code |
| `.atlas/ATLAS-2.0-PROGRESS.md` | Tracking progression |
| `.atlas/config.yml` | Config monorepo (Phase 4) |
| `CLAUDE.md` | Instructions Claude Code |

---

## Contact / Debug

Si tu es Claude et tu ne sais pas quoi faire:
1. Lis `.atlas/ATLAS-2.0-PROGRESS.md`
2. Trouve la première tâche `[ ]` non cochée
3. Exécute cette tâche
4. Update le fichier avec `[x]`
5. Continue jusqu'à fin de phase
