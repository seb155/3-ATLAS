# Smart Compact - Token Optimization

Effectue un /compact intelligent avec sauvegarde d'état pour récupération via /0-resume.

## Workflow Automatique

### 1. Vérifier le contexte actuel

```bash
# Afficher l'utilisation du contexte
/context
```

### 2. Sauvegarder l'état avant compact

Créer un fichier de session dans `.atlas/sessions/`:

```
Fichier: .atlas/sessions/compact-{YYYY-MM-DD-HHmm}.md
```

**Contenu à sauvegarder:**
- TodoWrite state actuel (tâches pending/in_progress)
- Fichiers en cours de modification
- Branche git et changements non commités
- Dernière erreur/résultat de test
- App/répertoire de focus

### 3. Exécuter /compact avec instructions ATLAS

```
/compact Préserver uniquement:
- Tâches actives du TodoWrite et leur progression
- Chemins des fichiers en cours de modification
- Résultats de tests et erreurs rencontrées
- Branche git: {branch} avec {n} fichiers modifiés
- Focus actuel: {app}/{directory}

Supprimer:
- Contenu des fichiers déjà commités
- Résultats d'exploration/recherche
- Outputs verbeux des outils
- Historique de conversation non pertinent
```

### 4. Afficher instructions de récupération

```
╔══════════════════════════════════════════════════════════════╗
║  ✅ COMPACT TERMINÉ                                          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  État sauvegardé: .atlas/sessions/compact-{timestamp}.md     ║
║                                                              ║
║  Pour reprendre:                                             ║
║  → /0-resume                                                 ║
║                                                              ║
║  Ou dans nouvelle conversation:                              ║
║  → "Continue depuis .atlas/sessions/compact-{timestamp}.md"  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

## Template de Sauvegarde

```markdown
# Session Compact - {timestamp}

## État au moment du compact

**Branch:** {git_branch}
**Fichiers modifiés:** {count}
**App focus:** {app_name}
**Répertoire:** {current_dir}

## Tâches TodoWrite

{todo_list_state}

## Fichiers en cours

{list_of_files_being_edited}

## Derniers résultats

### Tests
{test_results_summary}

### Erreurs
{recent_errors}

## Pour reprendre

1. Lire ce fichier
2. Restaurer le TodoWrite
3. Continuer depuis: {last_task}
```

## Quand utiliser /0-compact

| Situation | Action |
|-----------|--------|
| Contexte à ~50% | ✅ Exécuter /0-compact |
| Avant tâche complexe | ✅ Nettoyer le contexte |
| Après exploration longue | ✅ Garder seulement les résultats |
| Contexte à 95% | ⚠️ Trop tard, auto-compact déclenché |

## Notes

- Préférer /0-compact manuel à 50% plutôt qu'auto-compact à 95%
- L'auto-compact consomme ~45k tokens (22% de la fenêtre)
- Toujours vérifier `/context` avant de décider
