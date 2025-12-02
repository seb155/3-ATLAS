# Resume - Mode RECOVERY

Reprend après /compact, interruption, ou nouvelle conversation.

## Workflow de Récupération

### 1. Détecter la source de récupération

**Priorité de chargement:**
1. Argument fourni: `@.atlas/sessions/compact-{timestamp}.md`
2. Fichier le plus récent: `.atlas/sessions/compact-*.md`
3. État de session: `.dev/ai/session-state.json`
4. Mode dégradé: git status + CLAUDE.md

### 2. Charger le contexte essentiel

```
@CLAUDE.md
@.atlas/sessions/{latest-compact}.md (si existe)
@.dev/context/project-state.md
```

### 3. Afficher l'état de récupération

```
╔══════════════════════════════════════════════════════════════╗
║  🔄 MODE RECOVERY - Reprise de session                       ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Source: .atlas/sessions/compact-2025-12-02-1430.md          ║
║                                                              ║
║  État restauré:                                              ║
║  ├─ Branch: feature/new-api                                  ║
║  ├─ App: SYNAPSE                                             ║
║  ├─ Fichiers modifiés: 3                                     ║
║  └─ Tâches pending: 2                                        ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  TodoWrite restauré:                                         ║
║  ☑ Tâche 1 (completed)                                       ║
║  ▶ Tâche 2 (in_progress)                                     ║
║  ○ Tâche 3 (pending)                                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### 4. Restaurer le TodoWrite

Recréer l'état des tâches depuis le fichier de session:

```
TodoWrite avec l'état sauvegardé
```

### 5. Proposer la continuation

```
Je vois que tu travaillais sur: {last_task_description}

Dernière action: {last_action}

On continue?
```

## Récupération sans fichier de session

Si aucun fichier `.atlas/sessions/compact-*.md` n'existe:

### Mode Dégradé

1. **Lire git status**
```bash
git status --short
git log -3 --oneline
```

2. **Charger contexte minimal**
```
@CLAUDE.md
@.dev/context/project-state.md
```

3. **Demander le contexte**
```
Pas de session sauvegardée trouvée.

Contexte actuel:
- Branch: {branch}
- Fichiers modifiés: {files}
- Dernier commit: {commit_msg}

Sur quoi travaillais-tu?
```

## Pattern Document & Clear

Pour une récupération optimale entre sessions:

### Fin de session (avant /compact)
```
/0-compact
```

### Nouvelle session
```
/0-resume
```

### Nouvelle conversation (après timeout)
```
@CLAUDE.md @.atlas/sessions/compact-{date}.md
Continuons où on en était
```

## Fichiers chargés automatiquement

| Fichier | Toujours | Si existe |
|---------|----------|-----------|
| CLAUDE.md | ✅ | - |
| .atlas/sessions/compact-*.md | - | ✅ |
| .dev/context/project-state.md | ✅ | - |
| .dev/ai/session-state.json | - | ✅ |

## Notes

- Ce mode restaure le contexte COMPLET
- Utilisé automatiquement après /compact
- Préserve la continuité de la session
- Compatible avec le pattern Document & Clear
