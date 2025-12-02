<!-- 🔒 PROTECTED: Meta-rule - DO NOT MODIFY WITHOUT OWNER VALIDATION -->

# Règle 20: Documents Protégés - Validation Obligatoire

**Status:** OBLIGATOIRE
**Dernière mise à jour:** 2025-11-30
**Scope:** Tous les agents AI

---

## RÈGLE ABSOLUE

**Certains documents sont PROTÉGÉS et ne doivent JAMAIS être modifiés sans validation explicite du owner.**

---

## Documents Protégés 🔒

### Infrastructure Critique

| Document | Chemin | Raison |
|:---------|:-------|:-------|
| Registry | `.dev/infra/registry.yml` | Ports, services, réseaux |
| Architecture | `.dev/ARCHITECTURE.md` | Architecture système |
| Credentials | `.dev/context/credentials.md` | Secrets, mots de passe |
| Infrastructure | `.dev/infra/infrastructure.md` | Config infrastructure |

### Règles Agent

| Document | Chemin | Raison |
|:---------|:-------|:-------|
| Traefik | `.claude/agents/rules/10-*.md` | Routage obligatoire |
| URL Registry | `.claude/agents/rules/11-*.md` | Gestion URLs |
| Docker | `.claude/agents/rules/12-*.md` | Configuration réseau |
| **Cette règle** | `.claude/agents/rules/20-*.md` | Protection documents |

### Documentation Infrastructure

| Document | Chemin | Raison |
|:---------|:-------|:-------|
| Docker Compose | `docs/infrastructure/docker-compose-rules.md` | Règles Docker |
| Network | `docs/infrastructure/network-architecture.md` | Architecture réseau |
| Secrets | `docs/infrastructure/secrets-management.md` | Gestion secrets |
| Hardware | `docs/infrastructure/hardware-config.md` | Config matériel |

---

## Identification des Documents Protégés

Les documents protégés sont identifiés par:

1. **Header de protection** au début du fichier:
   ```
   <!-- 🔒 PROTECTED: ... DO NOT MODIFY WITHOUT OWNER VALIDATION -->
   ```
   ou pour YAML:
   ```yaml
   # 🔒 PROTECTED DOCUMENT - DO NOT MODIFY WITHOUT OWNER VALIDATION
   ```

2. **Présence dans cette liste**

3. **Pattern de chemin**:
   - `.dev/infra/*`
   - `.dev/context/credentials.md`
   - `.claude/agents/rules/*`
   - `docs/infrastructure/*`

---

## Comportement Attendu des Agents

### ✅ AUTORISÉ (Lecture)

- Lire le contenu des documents protégés
- Référencer les informations dans les réponses
- Suggérer des modifications

### ❌ INTERDIT (Sans Validation)

- Modifier directement le contenu
- Supprimer des fichiers protégés
- Renommer des fichiers protégés
- Changer la structure des fichiers protégés

### 🔄 PROCESSUS DE MODIFICATION

Si une modification est nécessaire:

1. **Identifier** le document comme protégé
2. **Proposer** la modification au owner
3. **Expliquer** pourquoi la modification est nécessaire
4. **Attendre** la validation explicite
5. **Exécuter** seulement après approbation

---

## Exemple de Proposition

```markdown
## 🔒 Modification Document Protégé

**Document:** `.dev/infra/registry.yml`
**Type de modification:** Ajout d'un nouveau port

**Changement proposé:**
- Ajouter port 4500 pour nouveau service X
- Raison: Nécessaire pour [explication]

**Impact:**
- Aucun conflit de port détecté
- Compatible avec la structure existante

**Voulez-vous que j'applique cette modification?**
```

---

## Sanctions

Un agent qui modifie un document protégé sans validation:
- La modification sera considérée comme non-autorisée
- Le owner peut demander un rollback
- L'agent doit expliquer pourquoi la règle a été ignorée

---

## Mise à Jour de Cette Règle

Cette règle elle-même est protégée. Pour l'étendre:
1. Proposer les nouveaux documents à protéger
2. Obtenir validation du owner
3. Mettre à jour la liste

---

*Cette règle assure l'intégrité des configurations critiques du système AXIOM.*
