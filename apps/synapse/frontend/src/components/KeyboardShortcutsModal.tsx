import { X, Keyboard } from 'lucide-react';

interface ShortcutItem {
    keys: string;
    description: string;
}

interface ShortcutCategory {
    title: string;
    shortcuts: ShortcutItem[];
}

interface KeyboardShortcutsModalProps {
    onClose: () => void;
}

export function KeyboardShortcutsModal({ onClose }: KeyboardShortcutsModalProps) {
    const categories: ShortcutCategory[] = [
        {
            title: 'Global',
            shortcuts: [
                { keys: 'Ctrl+K', description: 'Open Command Palette' },
                { keys: 'Ctrl+B', description: 'Toggle Sidebar' },
                { keys: 'Ctrl+\\', description: 'Toggle Dev Console' },
                { keys: 'Ctrl+/', description: 'Show keyboard shortcuts' },
                { keys: '/', description: 'Focus search' },
                { keys: '?', description: 'Show help' },
                { keys: 'Escape', description: 'Close modals / Clear selection' }
            ]
        },
        {
            title: 'Grid Navigation',
            shortcuts: [
                { keys: '↑↓←→', description: 'Navigate grid rows' },
                { keys: 'Enter', description: 'Open selected row details' },
                { keys: 'Ctrl+A', description: 'Select all rows' }
            ]
        },
        {
            title: 'Grid Tools',
            shortcuts: [
                { keys: 'Ctrl+F', description: 'Focus quick filter' },
                { keys: 'Ctrl+Shift+C', description: 'Toggle column manager' },
                { keys: 'Ctrl+Shift+F', description: 'Toggle filter presets' }
            ]
        }
    ];

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center animate-in fade-in duration-200">
            <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm transition-opacity" onClick={onClose} />

            <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-xl shadow-2xl flex flex-col max-h-[80vh] animate-in zoom-in-95 duration-200">
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-slate-800 rounded-lg text-mining-teal">
                            <Keyboard size={20} />
                        </div>
                        <h2 className="text-lg font-bold text-white">Keyboard Shortcuts</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Content */}
                < div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar" >
                    {
                        categories.map((category, idx) => (
                            <div key={idx}>
                                <h3 className="text-sm font-semibold text-mining-teal uppercase tracking-wider mb-3">
                                    {category.title}
                                </h3>
                                <div className="space-y-2">
                                    {category.shortcuts.map((shortcut, sidx) => (
                                        <div
                                            key={sidx}
                                            className="flex items-center justify-between px-4 py-2 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition-colors"
                                        >
                                            <span className="text-sm text-slate-300">{shortcut.description}</span>
                                            <kbd className="px-3 py-1 bg-slate-700 border border-slate-600 rounded text-xs font-mono text-mining-teal">
                                                {shortcut.keys}
                                            </kbd>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))
                    }
                </div >

                {/* Footer */}
                < div className="p-4 border-t border-slate-800 bg-slate-900/50" >
                    <p className="text-xs text-slate-500 text-center">
                        Press <kbd className="px-2 py-0.5 bg-slate-800 rounded text-mining-teal font-mono">Escape</kbd> or click outside to close
                    </p>
                </div >
            </div >
        </div >
    );
}
