import { useState, useRef, useEffect } from 'react';
import { Palette } from 'lucide-react';
import { useThemeStore } from '@/stores/useThemeStore';
import { getThemesByType, findThemeById } from '@/themes';

export function ThemeSelector() {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { activeThemeId, setTheme } = useThemeStore();
  const activeTheme = findThemeById(activeThemeId);
  const themesByType = getThemesByType();

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  const handleSelectTheme = (themeId: string) => {
    setTheme(themeId);
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded-lg hover:bg-accent transition-colors"
        aria-label="Toggle theme selector"
        title={`Current theme: ${activeTheme?.name || 'Unknown'}`}
      >
        <Palette className="h-5 w-5" />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 border border-border rounded-lg shadow-lg z-50" style={{backgroundColor: 'hsl(var(--card) / 0.95)', backdropFilter: 'blur(10px)'}}>
          {/* Dark Themes Section */}
          {themesByType.dark.length > 0 && (
            <div>
              <div className="px-3 py-2 text-xs font-semibold text-muted-foreground uppercase bg-muted/50">
                Dark Themes
              </div>
              {themesByType.dark.map((theme) => (
                <button
                  key={theme.id}
                  onClick={() => handleSelectTheme(theme.id)}
                  className={`w-full text-left px-3 py-2 text-sm hover:bg-muted transition-colors flex items-center justify-between ${
                    activeThemeId === theme.id ? 'bg-muted font-semibold' : ''
                  }`}
                >
                  <span>{theme.name}</span>
                  {activeThemeId === theme.id && <span className="text-primary">✓</span>}
                </button>
              ))}
            </div>
          )}

          {/* Light Themes Section */}
          {themesByType.light.length > 0 && (
            <div>
              <div className="px-3 py-2 text-xs font-semibold text-muted-foreground uppercase bg-muted/50">
                Light Themes
              </div>
              {themesByType.light.map((theme) => (
                <button
                  key={theme.id}
                  onClick={() => handleSelectTheme(theme.id)}
                  className={`w-full text-left px-3 py-2 text-sm hover:bg-muted transition-colors flex items-center justify-between ${
                    activeThemeId === theme.id ? 'bg-muted font-semibold' : ''
                  }`}
                >
                  <span>{theme.name}</span>
                  {activeThemeId === theme.id && <span className="text-primary">✓</span>}
                </button>
              ))}
            </div>
          )}

          {/* Divider if custom themes exist */}
          {useThemeStore.getState().customThemes.length > 0 && (
            <div className="h-px bg-border my-2" />
          )}

          {/* Custom Themes Section */}
          {useThemeStore.getState().customThemes.length > 0 && (
            <div>
              <div className="px-3 py-2 text-xs font-semibold text-muted-foreground uppercase bg-muted/50">
                Custom Themes
              </div>
              {useThemeStore.getState().customThemes.map((theme) => (
                <button
                  key={theme.id}
                  onClick={() => handleSelectTheme(theme.id)}
                  className={`w-full text-left px-3 py-2 text-sm hover:bg-muted transition-colors flex items-center justify-between ${
                    activeThemeId === theme.id ? 'bg-muted font-semibold' : ''
                  }`}
                >
                  <span>{theme.name}</span>
                  {activeThemeId === theme.id && <span className="text-primary">✓</span>}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
