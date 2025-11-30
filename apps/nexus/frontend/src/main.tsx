import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Initialize window.name for Excalidraw library support
// This prevents libraries.excalidraw.com from opening in a new tab
// when users click "Add to Excalidraw" on library items.
// See: https://github.com/excalidraw/excalidraw/issues/6778
if (!window.name) {
  window.name = 'nexus-excalidraw-app';
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
