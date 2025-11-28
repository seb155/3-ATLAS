import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './src/App';
// AG Grid styles are now handled via JS Theming API
import { setupAxiosInterceptors } from './src/services/axiosConfig';

// Initialize axios interceptors (Auth token + Project ID)
setupAxiosInterceptors();

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);