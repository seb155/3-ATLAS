# Dashboard - Status Session

Affiche le status de la session courante.

## Instructions

1. **Charger l'état de session:**
   - Lire `.dev/ai/session-state.json`
   - Lire `.dev/ai/agent-stats.json`

2. **Afficher le dashboard:**

```
📊 AXIOM Dashboard - Session Active
═══════════════════════════════════════════════════════

Session:    {current_session.id}
Mode:       {current_session.mode}
Démarré:    {current_session.started_at}
Durée:      {calculated_duration}

═══════════════════════════════════════════════════════

🎯 Focus: {current_session.focus}

📱 Apps Actives:
   • {app1} - {status}
   • {app2} - {status}

═══════════════════════════════════════════════════════

📝 Tâches cette session:
   ✓ Tâche complétée 1
   ✓ Tâche complétée 2
   → Tâche en cours

═══════════════════════════════════════════════════════

📁 Fichiers modifiés:
   M  path/to/file1.py
   M  path/to/file2.tsx
   A  path/to/new_file.py

═══════════════════════════════════════════════════════

💰 Stats Session:
   Tokens:  ~{estimate}
   Commits: {count}

═══════════════════════════════════════════════════════
```

3. **Vérifier git status:**
   ```bash
   git status --short
   ```

4. **Proposer actions:**
   > "Veux-tu continuer sur la tâche en cours, ou voir autre chose?"

## Notes

- Vue status uniquement
- Utiliser `/0-ship` pour commiter
- Utiliser `/0-progress` pour voir toutes les apps
