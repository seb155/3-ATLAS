# Excalidraw Integration in NEXUS

## Overview

NEXUS integrates Excalidraw (v0.18.0) for collaborative whiteboard drawing with full library support, real-time sync, and advanced UX features.

## Features Implemented

### 1. Drawing Management
- Create, edit, and delete drawings
- Hierarchical folder structure
- Auto-save with debouncing
- Thumbnail generation
- Version control

### 2. Library Integration
- Browse libraries from libraries.excalidraw.com
- Install libraries with confirmation prompt
- Persist libraries across sessions (localStorage)
- Share libraries across Drawing page and Notes editor
- Automatic library menu opening after installation

### 3. Advanced UX
- Collapsible sidebar (localStorage persistence)
- Fullscreen mode (keyboard shortcut: F)
- Inline rename (double-click)
- Auto-select new drawings
- Enhanced editable title with visual feedback

## Technical Architecture

### Components

**1. Drawing Page (`frontend/src/pages/Drawing.tsx`)**
- Main drawing canvas with sidebar
- Tree view for drawing organization
- ExcalidrawCanvas wrapper component

**2. Notes Editor Block (`frontend/src/components/editor/extensions/ExcalidrawBlock/`)**
- TipTap extension for embedding drawings in notes
- Inline and modal editing modes
- Synchronized with Drawing page

### Key Configuration

**window.name Setup (`frontend/src/main.tsx`)**
```typescript
// Prevents library browser from opening in new tab
if (!window.name) {
  window.name = 'nexus-excalidraw-app';
}
```

**ExcalidrawCanvas Component**
```typescript
const excalidrawRef = useRef<any>(null);

// Library state management
const [libraries, setLibraries] = useState<any[]>(() => {
  const saved = localStorage.getItem('excalidraw-libraries');
  return saved ? JSON.parse(saved) : [];
});

// Library installation handler
useEffect(() => {
  const handleHashChange = async () => {
    const hash = new URLSearchParams(window.location.hash.slice(1));
    const libraryUrl = hash.get('addLibrary');

    if (libraryUrl && excalidrawRef.current) {
      await excalidrawRef.current.updateLibrary({
        libraryItems: libraryUrl,
        merge: true,
        prompt: true,
        openLibraryMenu: true,
      });
      window.location.hash = '';
    }
  };

  window.addEventListener('hashchange', handleHashChange);
  handleHashChange();
  return () => window.removeEventListener('hashchange', handleHashChange);
}, []);
```

**Props Configuration**
```typescript
<Excalidraw
  ref={excalidrawRef}
  initialData={initialData}
  onChange={onChange}
  theme="dark"
  libraryReturnUrl={`${window.location.origin}${window.location.pathname}`}
  onLibraryChange={handleLibraryChange}
/>
```

## User Guide

### Creating a Drawing
1. Navigate to Drawing page
2. Click "New Drawing" button
3. Drawing is auto-selected in canvas
4. Edit title by clicking/hovering on title input

### Using Libraries
1. Click "Library" button in Excalidraw toolbar
2. Browse libraries at libraries.excalidraw.com
3. Click "Add to Excalidraw" on desired library
4. Confirm installation in prompt
5. Library menu opens automatically
6. Elements are available for use

### Keyboard Shortcuts
- `F` - Toggle fullscreen mode
- `Escape` - Exit fullscreen mode
- `Ctrl+S` - Save drawing (auto-save enabled)
- `Double-click` - Rename drawing in sidebar

### Fullscreen Mode
- Click maximize button or press `F`
- Canvas expands to full viewport
- Sidebar and header hidden
- Exit button in top-right corner
- Press `Escape` or click exit button to return

## Troubleshooting

### Library Installation Not Working
**Symptom:** Clicking "Add to Excalidraw" does nothing

**Solution:**
- Check browser console for errors
- Verify `window.name` is set in main.tsx
- Confirm `excalidrawRef` is passed to component
- Check hashchange listener is registered

### Libraries Not Persisting
**Symptom:** Libraries disappear after page refresh

**Solution:**
- Verify localStorage is enabled
- Check `onLibraryChange` callback is configured
- Inspect localStorage for `excalidraw-libraries` key

### Sidebar Not Collapsing
**Symptom:** Collapse button doesn't work

**Solution:**
- Check localStorage for `drawing-sidebar-collapsed` key
- Verify state management in component
- Clear localStorage and try again

## API Reference

### updateLibrary Method
```typescript
await excalidrawRef.current.updateLibrary({
  libraryItems: string | LibraryItem[],  // URL or array of items
  merge: boolean,                         // Merge vs replace
  prompt: boolean,                        // Show confirmation
  openLibraryMenu: boolean,              // Open menu after install
});
```

### Library Storage Format
```typescript
// localStorage key: 'excalidraw-libraries'
{
  libraryItems: LibraryItem[];
  version: number;
}
```

## Performance Considerations

- **Lazy Loading:** Excalidraw bundle (~2MB) loaded on demand
- **Debounced Auto-save:** 500ms delay to reduce API calls
- **localStorage Cache:** Libraries stored locally for instant access
- **HMR Compatible:** Hot module replacement works during development

## Version History

### v0.2.0 (2025-11-29)
- Library integration with hashchange listener
- Fullscreen mode with keyboard shortcuts
- Collapsible sidebar with persistence
- Inline rename functionality
- Auto-select new drawings
- Enhanced title editing UX

### v0.1.0 (Initial)
- Basic Excalidraw integration
- CRUD operations for drawings
- Tree view organization

## Related Documentation

- [Excalidraw Official Docs](https://docs.excalidraw.com)
- [Excalidraw API Reference](https://docs.excalidraw.com/docs/@excalidraw/excalidraw/api/props/)
- [TriliumNext Integration](./TRILIUM-INTEGRATION.md)
- [Backend API](../backend/README.md)

## Known Issues

None currently.

## Future Enhancements

- [ ] Backend sync for libraries (multi-device support)
- [ ] Collaborative real-time editing (Yjs integration)
- [ ] Custom library creation UI
- [ ] Drawing templates
- [ ] Export to multiple formats (SVG, PNG, PDF)
