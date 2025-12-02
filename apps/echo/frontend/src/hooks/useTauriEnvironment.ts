/**
 * Hook to detect if running in Tauri desktop environment.
 *
 * Provides capabilities detection for desktop-specific features:
 * - System audio capture (WASAPI loopback)
 * - Global hotkeys
 * - System tray integration
 */

import { useState, useEffect } from 'react';

export interface TauriEnvironment {
  /** Whether running in Tauri desktop app */
  isTauri: boolean;
  /** Whether detection is still loading */
  isLoading: boolean;
  /** Available capabilities based on environment */
  capabilities: {
    /** System audio capture (WASAPI loopback) */
    systemAudio: boolean;
    /** Global keyboard shortcuts */
    globalHotkeys: boolean;
    /** System tray integration */
    systemTray: boolean;
    /** Native file dialogs */
    nativeDialogs: boolean;
  };
}

/**
 * Detect if running in Tauri environment.
 *
 * Checks for the presence of Tauri globals injected by the runtime.
 */
function detectTauri(): boolean {
  if (typeof window === 'undefined') {
    return false;
  }

  // Tauri 2.0 injects __TAURI_INTERNALS__
  // Tauri 1.x injected __TAURI__
  return '__TAURI_INTERNALS__' in window || '__TAURI__' in window;
}

/**
 * Hook to detect Tauri environment and available capabilities.
 *
 * @example
 * ```tsx
 * function RecordPage() {
 *   const { isTauri, capabilities } = useTauriEnvironment();
 *
 *   return (
 *     <div>
 *       <button disabled={!capabilities.systemAudio}>
 *         Record System Audio
 *       </button>
 *     </div>
 *   );
 * }
 * ```
 */
export function useTauriEnvironment(): TauriEnvironment {
  const [isTauri, setIsTauri] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Detection is synchronous but we use effect for SSR safety
    const detected = detectTauri();
    setIsTauri(detected);
    setIsLoading(false);

    if (detected) {
      console.log('[ECHO] Running in Tauri desktop environment');
    } else {
      console.log('[ECHO] Running in web browser environment');
    }
  }, []);

  return {
    isTauri,
    isLoading,
    capabilities: {
      // Desktop features only available in Tauri
      systemAudio: isTauri,
      globalHotkeys: isTauri,
      systemTray: isTauri,
      nativeDialogs: isTauri,
    },
  };
}

/**
 * Check if running on Windows (for WASAPI-specific features).
 */
export function isWindows(): boolean {
  if (typeof window === 'undefined' || !window.navigator) {
    return false;
  }
  return window.navigator.userAgent.includes('Windows');
}

export default useTauriEnvironment;
