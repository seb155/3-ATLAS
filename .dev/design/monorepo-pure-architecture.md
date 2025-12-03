# Architecture Monorepo AXIOM - Structure Modulaire

**Date:** 2025-12-03
**Approche:** Monorepo pur avec extraction optionnelle

---

## Pourquoi cette approche ?

| Submodules | Monorepo Pur |
|------------|--------------|
| ❌ Nécessite repos externes | ✅ Tout dans un seul repo |
| ❌ Complexité de synchronisation | ✅ Un seul `git pull` |
| ❌ `--recurse-submodules` requis | ✅ Clone standard |
| ❌ Conflits de versions | ✅ Toujours synchronisé |
| ✅ Repos indépendants | ✅ Extraction possible plus tard |

---

## Structure Finale

```
AXIOM/                              # seb155/AXIOM (monorepo unique)
│
├── modules/                        # ← Nouveau! Composants réutilisables
│   ├── forge/                      # Infrastructure partagée
│   ├── atlas-framework/            # Framework Claude Code
│   └── README.md
│
├── apps/                           # Applications
│   ├── synapse/                    # MBSE Platform
│   ├── nexus/                      # Knowledge Graph
│   ├── cortex/                     # AI Ecosystem
│   ├── apex/                       # Enterprise Portal (future)
│   └── echo/                       # Voice Interface (future)
│
├── .claude → modules/atlas-framework/claude/  # Symlink
│
├── .dev/                           # Context & tracking
├── docs/                           # Documentation
├── scripts/
│   ├── migration/                  # Scripts si extraction future
│   └── dev/                        # Scripts développement
│
└── CLAUDE.md
```

---

## Avantages

1. **Simplicité** : Un seul repo, un seul clone, un seul historique
2. **Cohérence** : Tous les composants évoluent ensemble
3. **Flexibilité** : Extraction vers repos séparés possible à tout moment
4. **CI/CD unifié** : Une seule pipeline GitHub Actions
5. **Pas de dépendances externes** : Fonctionne offline

---

## Extraction Future (si nécessaire)

Si un jour tu veux extraire un module vers un repo séparé :

```bash
# Utiliser git filter-repo pour extraire avec historique
git filter-repo --subdirectory-filter modules/forge --force

# Ou simplement copier (sans historique)
cp -r modules/forge /nouveau/repo/
```

---

## Migration depuis structure actuelle

```bash
# Créer le dossier modules/
mkdir -p modules

# Déplacer forge
mv forge modules/forge

# Copier .atlas vers modules/atlas-framework
cp -r .atlas modules/atlas-framework

# Mettre à jour le symlink .claude
rm -f .claude
ln -sf modules/atlas-framework/claude .claude
```

---

## Quand utiliser des submodules ?

Utilise des submodules UNIQUEMENT si :
- [ ] Tu partages un composant entre PLUSIEURS projets distincts
- [ ] Une équipe externe maintient un composant
- [ ] Tu veux publier un composant en open-source séparément

Pour un projet personnel/solo, le monorepo pur est plus simple.
