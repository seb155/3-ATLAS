# Resume - Mode RECOVERY

Reprend après une interruption (ex: /compact, crash, timeout).

## Instructions

1. **Détecter l'état précédent:**
   - Lire `.dev/ai/session-state.json`
   - Vérifier si `current_session` était actif

2. **Afficher l'état de récupération:**

```
🔄 Mode RECOVERY - Reprise de session
═══════════════════════════════════════════════════════

Session interrompue: {current_session.id}
Mode:               {current_session.mode}
Focus:              {current_session.focus}
Apps actives:       {active_apps}

Tâches en cours au moment de l'interruption:
  → (à déterminer depuis le contexte)

═══════════════════════════════════════════════════════
```

3. **Recharger le contexte complet:**
   - Lire tous les fichiers de contexte des apps actives
   - Lire les fichiers hot modifiés récemment

4. **Proposer de continuer:**
   > "Je vois que tu travaillais sur [X]. On reprend là où tu en étais?"

5. **Garder le même session ID:**
   - Ne pas créer nouvelle session
   - Marquer comme "recovered"

## Notes

- Ce mode restaure le contexte COMPLET
- Utilisé automatiquement après /compact
- Préserve la continuité de la session
