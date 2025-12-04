# Règles de Recherche Web

## Mode: CONFIGURABLE & ÉCONOMIQUE

### Configuration

Lire la config dans `.claude/config/web-search.json` ou `.atlas/config/web-search.json` (override projet).

```json
{
  "web_search": {
    "auto_tech": false,      // Recherche auto tech/dev
    "auto_temporal": false,  // Recherche auto dates récentes
    "retry_threshold": 2,    // Échecs avant proposition
    "propose_on_failure": true
  }
}
```

---

## Comportement par Défaut (économique)

1. **NE PAS chercher automatiquement** sauf si `auto_*: true` dans la config
2. **Après N tentatives échouées** (défaut: 2) → Proposer recherche
3. **Si incertain sur info récente** → Proposer recherche (ne pas faire seul)

---

## Quand PROPOSER une recherche (mode économique)

Utiliser ce format:

> 🔍 **Recherche web suggérée**
> Je ne suis pas certain de [sujet]. Ma connaissance date de janvier 2025.
> **Veux-tu que je cherche sur internet?** (oui/non)

**Situations de proposition:**
- "Je ne suis pas sûr de la version actuelle de X..."
- "Ma connaissance pourrait être obsolète pour Y..."
- "J'ai échoué à [tâche] plusieurs fois. Une recherche web pourrait aider?"
- Questions sur événements post-janvier 2025

---

## Quand rechercher automatiquement

### SI `auto_tech: true`

Utiliser `WebSearch` sans demander pour:
- Versions/releases récentes de frameworks/libs
- Documentation officielle 2024-2025
- Best practices et patterns actuels
- Bugs/issues connus récents
- Changements d'API récents

### SI `auto_temporal: true`

Utiliser `WebSearch` sans demander pour:
- Mention explicite de dates récentes (2024, 2025, "cette année")
- Questions sur "l'état actuel de..."
- "Qu'est-ce qui a changé dans..."
- "Les dernières nouvelles sur..."
- Toute question où janvier 2025 serait clairement obsolète

---

## Format après Recherche

Quand tu effectues une recherche web:

1. **Cite TOUJOURS les sources** avec liens markdown
2. **Indique la date** des informations trouvées
3. **Compare** avec tes connaissances si différence notable
4. **Mentionne** si l'info contredit ce que tu savais

Exemple:
```markdown
Selon [Source](url) (consulté décembre 2025):
- React 19.1 est sorti en novembre 2025
- Nouveauté: Server Components sont maintenant stables

> Note: Ma connaissance (janvier 2025) mentionnait React 18.x comme dernière version stable.
```

---

## Toggle Rapide

Utiliser `/0-web-toggle` pour changer rapidement:
- `/0-web-toggle` - Voir état actuel
- `/0-web-toggle on` - Activer tout (tech + temporel)
- `/0-web-toggle off` - Mode économique (défaut)
- `/0-web-toggle tech` - Toggle uniquement auto_tech

---

## Coûts

- WebSearch: $10 / 1000 recherches
- Mode économique: ~$1.50-3/mois
- Mode auto complet: ~$6-15/mois
