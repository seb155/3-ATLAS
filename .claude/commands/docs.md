# /docs

Genere ou met a jour la documentation.

## Usage

```text
/docs              # Met a jour la doc de l'app courante
/docs [sujet]      # Doc specifique
/docs api          # Documentation API
/docs readme       # Met a jour le README
```

## Actions

1. DOC-WRITER analyse le code
2. Genere/met a jour la documentation
3. Suit les conventions du projet
4. Integre avec Docsify

## Agent Invoque

- DOC-WRITER (haiku) - Generation de documentation

## Types de Documentation

| Type | Output |
|------|--------|
| `api` | Documentation OpenAPI/Swagger |
| `readme` | README.md du module |
| `component` | Doc des composants React |
| `guide` | Guide utilisateur |
| `reference` | Reference technique |

## Emplacement

```text
docs/
├── apps/
│   ├── synapse.md
│   ├── nexus.md
│   ├── prism.md
│   └── atlas.md
├── developer-guide/
├── reference/
└── workflows/
```

## Exemple

```text
User: /docs api

DOC-WRITER:
"Generation de documentation API...

App detectee: SYNAPSE (backend)
Framework: FastAPI (OpenAPI auto)

Actions:
1. Export OpenAPI schema
2. Generation doc Markdown
3. Mise a jour docs/reference/api-synapse.md

Documentation generee:

# SYNAPSE API Reference

## Authentication
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh

## Projects
- GET /api/v1/projects
- POST /api/v1/projects
- GET /api/v1/projects/{id}
...

Documentation mise a jour dans docs/reference/api-synapse.md
Accessible sur http://localhost:3080/#/reference/api-synapse"
```
