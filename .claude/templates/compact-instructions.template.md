# Compact Instructions Template

Template pour generer des instructions optimales pour `/compact`.

---

## Format Standard

```
Preserve contexte session:

Projet: {project_name}
Branch: {git_branch}
Checkpoint: {latest_checkpoint_path}

Taches en cours:
{active_todos_formatted}

Fichiers hot:
{hot_files_list}

Decisions cles:
{key_decisions_summary}

Recovery: /0-resume
NOTE: Checkpoint pre-compact cree automatiquement.
```

---

## Exemples

### Dev Session
```
Preserve contexte dev:
- Projet: AXIOM/apps/synapse
- Feature: Auth JWT
- Fichiers: auth.py, middleware.py
- Decision: JWT + refresh tokens
- Recovery: /0-resume
```

### Debug Session
```
Preserve contexte debug:
- Bug: API timeout /api/users
- Hypotheses: DB, N+1, memory
- Resultat: N+1 confirme
- Fix: eager loading
- Recovery: /0-resume
```

---

## Rules

1. Max 15 lignes
2. Bullet points
3. Paths relatifs
4. Toujours terminer par recovery

---

*Template v1.0*
