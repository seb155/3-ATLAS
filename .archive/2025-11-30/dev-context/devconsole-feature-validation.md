# DevConsole V3 - Feature Validation & Testing Plan

**Date:** 2025-11-24  
**Status:** DRAFT - Requires User Approval  
**Version:** 3.0.0

---

## 🎯 Problèmes Identifiés

Selon l'utilisateur, plusieurs features ne fonctionnent pas correctement:
- ✗ Filtres (level, source, topic, discipline, time range)
- ✗ Items cliquables (workflows, logs, assets)
- ✗ Interprétation des workflows
- ✗ Navigation vers assets depuis logs
- ✗ Manque de tests automatisés (backend + frontend)

---

## 📋 Features Attendues (selon documentation)

### 1. **Filtration Multi-critères**
| Feature | Implémentation Actuelle | Test Requis |
|---------|------------------------|-------------|
| **Level** (DEBUG/INFO/WARN/ERROR) | ✅ `FilterBar.tsx` ligne 39-49 | ⚠️ Manque tests |
| **Source** (FRONTEND/BACKEND) | ✅ `FilterBar.tsx` ligne 52-60 | ⚠️ Manque tests |
| **Topic** (ASSETS/RULES/CABLES) | ❌ NON IMPLÉMENTÉ | ⚠️ À CRÉER |
| **Discipline** (PROCESS/ELEC/AUTO) | ❌ NON IMPLÉMENTÉ | ⚠️ À CRÉER |
| **Time Range** (5M/1H/24H) | ✅ `FilterBar.tsx` ligne 63-72 | ⚠️ Manque tests |
| **Search Text** | ✅ `FilterBar.tsx` ligne 18-36 | ⚠️ Manque tests |
| **Workflows Only** | ✅ `FilterBar.tsx` ligne 75-83 | ⚠️ Manque tests |

**Problème détecté**: `topic` et `discipline` sont dans le `DevConsoleFilters` type mais **ne sont pas implémentés dans l'UI**.

---

### 2. **Navigation & Cliquabilité**
| Feature | Implémentation Actuelle | Test Requis |
|---------|------------------------|-------------|
| Cliquer sur un log | ✅ `TimelinePanel.tsx` ligne 173 | ⚠️ Manque tests |
| Cliquer sur un workflow | ✅ `TimelinePanel.tsx` ligne 71 | ⚠️ Manque tests |
| Expand/Collapse workflows | ✅ `TimelinePanel.tsx` ligne 38-39 | ⚠️ Manque tests |
| Navigation vers asset (entityRoute) | ❓ `DetailsPanel.tsx` (à vérifier) | ⚠️ Manque tests |
| Navigation depuis SmartPayloadViewer | ❓ À VÉRIFIER | ⚠️ Manque tests |

**Problème détecté**: Les `entityRoute` et `entityTag` sont définis dans le type mais leur utilisation n'est pas claire.

---

### 3. **Workflows & Actions**
| Feature | Backend | Frontend | Test |
|---------|---------|----------|------|
| `ActionLogger.start_action()` | ✅ Existe | ✅ Store grouping | ⚠️ Test backend uniquement |
| `ActionLogger.log_step()` | ✅ Existe | ✅ Affichage | ⚠️ Test backend uniquement |
| `ActionLogger.complete_action()` | ✅ Existe | ✅ Status update | ⚠️ Test backend uniquement |
| Grouping par `actionId` | ✅ Backend | ✅ `useDevConsoleStore.ts` ligne 243-284 | ❌ AUCUN TEST |

**Problème détecté**: Pas de tests d'intégration backend ↔ frontend pour workflows.

---

### 4. **WebSocket Real-time**
| Feature | Implémentation | Test |
|---------|---------------|------|
| Connexion WebSocket | ✅ `useWebSocketConnection` hook | ❌ AUCUN TEST |
| Reconnexion auto | ❓ À VÉRIFIER | ❌ AUCUN TEST |
| Affichage status connexion | ✅ `DevConsoleV3.tsx` ligne 154-168 | ❌ AUCUN TEST |
| Broadcast logs en temps réel | ✅ Backend via Loki | ❌ AUCUN TEST |

---

### 5. **Performance & UX**
| Feature | Doc Says | Implémentation | Test |
|---------|---------|---------------|------|
| Log pruning (max 1000) | ✅ Documenté | ✅ `useDevConsoleStore.ts` maxLogs | ❌ AUCUN TEST |
| Filter memoization | ✅ Documenté | ❓ À VÉRIFIER | ❌ AUCUN TEST |
| Virtual scrolling | ❌ Déféré | N/A | N/A |
| Auto-scroll | ✅ Documenté | ❓ À VÉRIFIER | ❌ AUCUN TEST |

---

## 🧪 Plan de Tests Automatisés

### **Phase 1: Tests Backend (Python/pytest)**

#### A. ActionLogger & WorkflowEngine
```python
# tests/test_action_logger.py
- test_start_action_creates_action_id()
- test_log_step_groups_by_action_id()
- test_complete_action_sets_status()
- test_fail_action_stops_workflow()
- test_action_stats_calculation()
```

#### B. WebSocket Logging
```python
# tests/test_websocket_logging.py
- test_websocket_sends_log_on_action()
- test_websocket_broadcast_to_all_clients()
- test_websocket_reconnection_handling()
```

#### C. Log Enrichment
```python
# tests/test_log_enrichment.py
- test_user_extracted_from_jwt()
- test_topic_auto_detected_from_url()
- test_entity_route_included_in_log()
- test_response_time_calculated()
```

---

### **Phase 2: Tests Frontend (Vitest + React Testing Library)**

#### A. Zustand Store Tests
```typescript
// src/test/useDevConsoleStore.test.ts
describe('DevConsoleStore', () => {
  test('addLog should add log to array')
  test('addLog should prune when exceeds maxLogs')
  test('getFilteredLogs respects level filter')
  test('getFilteredLogs respects source filter')
  test('getFilteredLogs respects timeRange filter')  // ⚠️ CRITICAL
  test('getFilteredLogs respects searchText filter')
  test('getFilteredWorkflows groups by actionId')
  test('toggleWorkflow expands/collapses workflow')
})
```

#### B. Component Tests
```typescript
// src/components/DevConsole/FilterBar.test.tsx
describe('FilterBar', () => {
  test('level filter updates store')
  test('source filter updates store')
  test('time range filter updates store')
  test('search input updates store')
  test('reset button clears all filters')
})

// src/components/DevConsole/TimelinePanel.test.tsx
describe('TimelinePanel', () => {
  test('displays logs when not in workflow mode')
  test('displays workflows when showOnlyWorkflows is true')
  test('clicking log calls selectLog')
  test('clicking workflow header toggles expansion')
})

// src/components/DevConsole/DetailsPanel.test.tsx
describe('DetailsPanel', () => {
  test('displays selected log details')
  test('displays entity navigation button if entityRoute exists')
  test('SmartPayloadViewer detects asset tags')
  test('clicking entity button navigates to route')
})
```

#### C. WebSocket Integration Tests
```typescript
// src/hooks/useWebSocketConnection.test.ts
describe('WebSocket Connection', () => {
  test('connects on mount')
  test('reconnects after disconnect')
  test('updates isConnected state')
  test('adds logs to store on message')
  test('disconnects on unmount')
})
```

---

### **Phase 3: Tests d'Intégration E2E (Playwright - OPTIONNEL)**

```typescript
// e2e/devconsole.spec.ts
test('import workflow creates logs in real-time', async ({ page }) => {
  // 1. Open DevConsole
  // 2. Trigger import
  // 3. Verify logs appear in timeline
  // 4. Verify workflow groups correctly
  // 5. Click workflow → verify expansion
  // 6. Click log → verify details panel
})

test('filters work correctly', async ({ page }) => {
  // 1. Generate logs at different levels
  // 2. Apply ERROR filter → verify only ERROR logs visible
  // 3. Apply time filter → verify old logs hidden
})
```

---

## 🔍 Features Manquantes à Implémenter

### 1. **Topic Filter (Multi-select)**
**Fichier**: `FilterBar.tsx`  
**Ajout requis**:
```tsx
// Multi-select dropdown for topics
<MultiSelect
  options={['ASSETS', 'RULES', 'CABLES', 'IMPORT', 'AUTH', 'PROJECT', 'SYSTEM']}
  value={filters.topics} // Note: need to change type from string to string[]
  onChange={(selected) => setFilter('topics', selected)}
/>
```

### 2. **Discipline Filter (Multi-select)**
**Fichier**: `FilterBar.tsx`  
**Ajout requis**:
```tsx
// Multi-select dropdown for disciplines
<MultiSelect
  options={['PROCESS', 'ELECTRICAL', 'AUTOMATION', 'MECHANICAL', 'PROJECT', 'PROCUREMENT']}
  value={filters.disciplines}
  onChange={(selected) => setFilter('disciplines', selected)}
/>
```

### 3. **SmartPayloadViewer Entity Detection**
**Fichier**: `DetailsPanel.tsx`  
**Status**: Documenté mais **à vérifier** si implémenté.

### 4. **Auto-scroll Intelligence**
**Fichier**: `TimelinePanel.tsx`  
**Status**: Documenté mais **à vérifier** si implémenté.

---

## 📊 Matrice de Décision

| Feature | Priorité | Effort | Valeur | Recommandation |
|---------|---------|--------|--------|----------------|
| **Topic Filter UI** | 🔴 HIGH | 2h | HIGH | ✅ IMPLÉMENTER |
| **Discipline Filter UI** | 🟡 MEDIUM | 2h | MEDIUM | ✅ IMPLÉMENTER |
| **Backend Tests** | 🔴 HIGH | 4h | HIGH | ✅ CRÉER |
| **Frontend Tests** | 🔴 HIGH | 6h | HIGH | ✅ CRÉER |
| **E2E Tests** | 🟢 LOW | 8h | MEDIUM | ⏸️ DÉFÉRER |
| **SmartPayloadViewer** | 🟡 MEDIUM | 3h | HIGH | ⚠️ VÉRIFIER D'ABORD |
| **Auto-scroll** | 🟡 MEDIUM | 2h | MEDIUM | ⚠️ VÉRIFIER D'ABORD |

**Effort Total (sans E2E)**: ~19 heures  
**Effort Total (avec E2E)**: ~27 heures

---

## 🎯 Proposition d'Approche (3 Phases)

### **Phase 1: Audit & Vérification (2-3h)**
1. ✅ Tester manuellement toutes les features existantes
2. ✅ Vérifier si `SmartPayloadViewer` et auto-scroll fonctionnent
3. ✅ Documenter ce qui est cassé vs ce qui manque
4. ✅ Prioriser les fixes

### **Phase 2: Implémentation Features Manquantes (4-6h)**
1. ✅ Ajouter Topic filter (multi-select)
2. ✅ Ajouter Discipline filter (multi-select)
3. ✅ Implémenter auto-scroll si manquant
4. ✅ Implémenter SmartPayloadViewer si manquant

### **Phase 3: Tests Automatisés (10-12h)**
1. ✅ Backend: ActionLogger, WorkflowEngine, WebSocket (6h)
2. ✅ Frontend: Store, Components, Hooks (6h)
3. ⏸️ E2E: Playwright tests (optionnel, 8h)

---

## ✅ Critères de Succès

### **Fonctionnel**
- [ ] Tous les filtres documentés fonctionnent (level, source, topic, discipline, time, search)
- [ ] Workflows se groupent correctement par `actionId`
- [ ] Items cliquables ouvrent le panneau de détails
- [ ] Navigation vers assets fonctionne depuis logs
- [ ] WebSocket se connecte et se reconnecte automatiquement
- [ ] Logs apparaissent en temps réel

### **Tests**
- [ ] Backend: 80%+ coverage sur `action_logger.py`, `workflow_engine.py`
- [ ] Frontend: 80%+ coverage sur `useDevConsoleStore.ts`
- [ ] Frontend: Tests pour `FilterBar`, `TimelinePanel`, `DetailsPanel`
- [ ] CI/CD: Tests executent automatiquement (GitHub Actions)

### **Documentation**
- [ ] `devconsole-v3.md` mis à jour avec features réelles
- [ ] Tests documentés dans `README.md`
- [ ] Workflow de test documenté (`/08-run-tests`)

---

## 🤔 Questions Pour L'Utilisateur

1. **Priorité**: Quelle phase veux-tu attaquer en premier?
   - A) Phase 1 (Audit/Vérification) - 2-3h
   - B) Phase 2 (Features manquantes) - 4-6h
   - C) Phase 3 (Tests automatisés) - 10-12h
   - D) Tout en séquence (16-21h total)

2. **Filters**: Veux-tu vraiment les filtres "Topic" et "Discipline" ou préfères-tu simplifier?
   - Les filtres actuels (level, source, time, search) sont peut-être suffisants?

3. **Tests E2E**: Playwright est-il nécessaire maintenant ou on se concentre sur unit/integration tests?

4. **Cassé vs Manquant**: Selon toi, qu'est-ce qui est **cassé** (fonctionnait avant) vs **manquant** (jamais implémenté)?

5. **Use Cases**: Quels sont tes 3 use cases principaux pour DevConsole?
   - Exemple: "Voir les erreurs d'import", "Débugger règles qui échouent", etc.

---

**Prochaines Étapes**: Attendre validation utilisateur avant d'exécuter.
