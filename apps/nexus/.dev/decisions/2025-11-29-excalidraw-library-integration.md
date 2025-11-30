# ADR: Excalidraw Library Integration Architecture

**Date:** 2025-11-29
**Status:** Accepted
**Deciders:** Development Team

## Context

NEXUS needed full integration with Excalidraw's library system to allow users to install pre-made shapes and elements from libraries.excalidraw.com. Initial implementation failed because:

1. Library browser opened in new tab (unusable)
2. "Add to Excalidraw" button did nothing
3. No handling of redirect flow from library browser

## Decision

Implemented a three-part solution:

### 1. window.name Configuration
Set `window.name = 'nexus-excalidraw-app'` in main.tsx to instruct Excalidraw to redirect to same tab instead of opening new one.

### 2. useRef for API Access
Used `useRef` to obtain reference to Excalidraw's imperative API, enabling programmatic calls to `updateLibrary()`.

### 3. hashchange Event Listener
Implemented event listener to detect when library browser redirects back with `#addLibrary=<url>` hash parameter, then trigger library installation.

## Alternatives Considered

### Alternative 1: Backend Library Proxy
**Rejected:** Too complex for MVP, adds unnecessary latency, requires database schema changes.

### Alternative 2: Custom Library Browser
**Rejected:** Reinventing the wheel, maintenance burden, incompatible with Excalidraw ecosystem.

### Alternative 3: postMessage API
**Rejected:** Doesn't work with redirect-based flow used by libraries.excalidraw.com.

## Consequences

### Positive
- ✅ Full compatibility with official Excalidraw library ecosystem
- ✅ No backend changes required (MVP-friendly)
- ✅ Works in both Drawing page and Notes editor
- ✅ localStorage persistence (works offline)
- ✅ Simple, maintainable implementation (~40 lines per component)

### Negative
- ❌ Libraries not synced across devices (localStorage only)
- ❌ Depends on hash-based navigation (could conflict with future routing)
- ❌ Requires users to allow popups/redirects (browser security)

### Neutral
- Libraries stored in localStorage (plan backend sync for v0.3.0)
- Hash parameters cleaned after installation (no URL pollution)

## Implementation Details

**Files Modified:**
- `frontend/src/main.tsx` (window.name setup)
- `frontend/src/pages/Drawing.tsx` (ref + hashchange)
- `frontend/src/components/editor/extensions/ExcalidrawBlock/ExcalidrawBlockNode.tsx` (ref + hashchange)

**Total LOC:** ~80 lines added

**Testing:** Manual testing confirms:
1. Library browser opens in same tab
2. "Add to Excalidraw" triggers installation prompt
3. Libraries persist across page refreshes
4. No console errors

## References

- [Excalidraw Issue #6778](https://github.com/excalidraw/excalidraw/issues/6778)
- [Excalidraw API Docs](https://docs.excalidraw.com/docs/@excalidraw/excalidraw/api/props/excalidraw-api)
- [Obsidian Plugin Implementation](https://github.com/zsviczian/obsidian-excalidraw-plugin/issues/2126)
