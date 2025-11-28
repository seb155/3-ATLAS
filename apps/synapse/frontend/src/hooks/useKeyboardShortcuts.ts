import { useState, useEffect } from 'react';

export interface KeyboardShortcut {
    key: string;
    ctrl?: boolean;
    shift?: boolean;
    alt?: boolean;
    description: string;
    category: 'global' | 'grid' | 'navigation';
    action: () => void;
}

interface UseKeyboardShortcutsProps {
    shortcuts: KeyboardShortcut[];
    enabled?: boolean;
}

export function useKeyboardShortcuts({ shortcuts, enabled = true }: UseKeyboardShortcutsProps) {
    const [isHelpOpen, setIsHelpOpen] = useState(false);

    useEffect(() => {
        if (!enabled) return;

        const handleKeyDown = (e: KeyboardEvent) => {
            // Check if user is typing in an input
            const target = e.target as HTMLElement;
            const isInput = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable;

            for (const shortcut of shortcuts) {
                const ctrlMatch = shortcut.ctrl ? e.ctrlKey || e.metaKey : !e.ctrlKey && !e.metaKey;
                const shiftMatch = shortcut.shift ? e.shiftKey : !e.shiftKey;
                const altMatch = shortcut.alt ? e.altKey : !e.altKey;
                const keyMatch = e.key.toLowerCase() === shortcut.key.toLowerCase();

                if (ctrlMatch && shiftMatch && altMatch && keyMatch) {
                    // Allow Ctrl+F in inputs (browser default)
                    if (shortcut.key === 'f' && shortcut.ctrl && !shortcut.shift && isInput) {
                        continue;
                    }

                    e.preventDefault();
                    shortcut.action();
                    return;
                }
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [shortcuts, enabled]);

    return {
        isHelpOpen,
        setIsHelpOpen
    };
}

// Predefined shortcut definitions
export const GLOBAL_SHORTCUTS = {
    HELP: { key: '/', ctrl: true, category: 'global' as const },
    QUICK_FILTER: { key: 'f', ctrl: true, category: 'grid' as const },
    COLUMN_MANAGER: { key: 'c', ctrl: true, shift: true, category: 'grid' as const },
    FILTER_PRESETS: { key: 'f', ctrl: true, shift: true, category: 'grid' as const },
    ESCAPE: { key: 'Escape', category: 'global' as const },
};
