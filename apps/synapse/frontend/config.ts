export const API_URL = import.meta.env.VITE_API_URL || '';

// WebSocket URL (derived from API URL)
const getWsUrl = () => {
  const apiUrl = API_URL || window.location.origin;
  return apiUrl.replace(/^http/, 'ws');
};

export const WS_URL = getWsUrl();
