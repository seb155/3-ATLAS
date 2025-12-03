# Changelog

All notable changes to the Nexus project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Phase 2: Notes/Wiki System (Dec 2025)
- TipTap rich text editor
- Wiki links with backlinks
- Full-text search

## [0.2.0] - 2025-11-29

### Added - Excalidraw Enhancements
- **Library Integration**: Full support for installing libraries from libraries.excalidraw.com
  - Configured `window.name` to prevent new tabs
  - Added `hashchange` event listener for library installation
  - Implemented `updateLibrary()` API calls with confirmation prompts
  - localStorage persistence for installed libraries

- **Advanced UX Features**:
  - Collapsible sidebar with localStorage state persistence
  - Fullscreen mode with `F` keyboard shortcut and `Escape` to exit
  - Inline rename via double-click in sidebar tree
  - Auto-selection of newly created drawings
  - Enhanced title input with hover/focus visual feedback

### Changed
- ExcalidrawCanvas component now uses `useRef` to access Excalidraw API
- Both Drawing.tsx and ExcalidrawBlockNode.tsx share library state via localStorage

### Fixed
- Library menu no longer opens in new tab
- "Add to Excalidraw" button now functional
- New drawings automatically selected and displayed

## [0.1.0-alpha] - 2025-11-27

### Added - Phase 1: Foundation
- React 19 + Vite 7 + TypeScript 5.9 project setup
- Tailwind CSS 4 with custom design system
- VSCode-like layout (AppLayout, Sidebar, TopBar, StatusBar)
- React Router DOM 7 with 6 pages (Dashboard, Notes, Tasks, Roadmap, Graph, Settings)
- Zustand state management (useAppStore, useAuthStore, useThemeStore)
- Development server on port 5173
- Path aliases (`@/*` → `./src/*`)
- Comprehensive documentation structure (`.dev/`, `docs/`, `CLAUDE.md`)
- Git repository initialization

### Added - Phase 1.5: Visual Polish
- Dynamic theme system with light/dark mode toggle
- 13 pre-built themes (6 dark, 6 light, 1 custom template)
- Theme persistence via localStorage
- Enhanced UI component library:
  - `Badge.tsx` - Status indicators with variants
  - `Button.tsx` - Enhanced with loading states
  - `Card.tsx` - Glass morphism variants
  - `StatCard.tsx` - Dashboard statistics
  - `Skeleton.tsx` - Loading placeholders with shimmer
- Dashboard visual overhaul with animated gradients
- All pages enhanced with rich preview content
- Smooth 60fps animations and micro-interactions
- Vercel/Linear-inspired design polish
- Hover effects and visual utilities

### Technical Stack
- React 19.2.0
- TypeScript 5.9.7
- Vite 7.2.4
- Tailwind CSS 4.1.17
- React Router DOM 7.9.6
- Zustand 5.0.8
- TanStack Query 5.90.11
- Lucide React 0.555.0

### Documentation
- Complete project state tracking (`.dev/context/project-state.md`)
- Phase 1 & 1.5 retrospective (`.dev/context/phase-1-retrospective.md`)
- Phase 2 implementation plan (`.dev/roadmap/phase-2-implementation-plan.md`)
- Daily development journals (`.dev/journal/`)
- Comprehensive AI workflows (`.agent/workflows/`)
- Design system documentation (`docs/design-system/`)

### Infrastructure
- Build system validated (TypeScript + Vite)
- Strict TypeScript configuration
- ESLint 9.39.1 with TypeScript support
- Git repository with semantic commits
- Development tracking structure

### Performance
- 60fps animations via GPU-accelerated transforms
- Optimized CSS transitions
- Efficient theme switching
- Minimal bundle size

## [0.0.0] - 2025-11-26

### Initial
- Project conception
- Repository created (private)
- Planning and architecture design

---

[Unreleased]: https://github.com/seb155/Nexus/compare/v0.1.0-alpha...HEAD
[0.1.0-alpha]: https://github.com/seb155/Nexus/releases/tag/v0.1.0-alpha
[0.0.0]: https://github.com/seb155/Nexus/commits/main
