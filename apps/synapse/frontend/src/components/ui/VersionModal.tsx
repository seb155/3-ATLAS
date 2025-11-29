import { X, Copy, Check, ExternalLink } from 'lucide-react';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { VERSION } from '../config/version';

interface VersionModalProps {
    onClose: () => void;
}

export function VersionModal({ onClose }: VersionModalProps) {
    const [copied, setCopied] = useState(false);

    const versionInfo = `SYNAPSE Version Information
  
Frontend:  v${VERSION.app}+${VERSION.gitHash}#${VERSION.buildNumber}
Build:     ${new Date(VERSION.buildDate).toLocaleString()}

Current Sprint: v0.2.2 - UX Professional
Next Sprint:    v0.2.3 - 3-Tier Asset Model`;

    const handleCopy = () => {
        navigator.clipboard.writeText(versionInfo);
        setCopied(true);
        toast.success('Version info copied to clipboard');
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={onClose}
        >
            <div
                className="bg-slate-900 border border-slate-700 rounded-xl shadow-2xl w-[500px] max-h-[80vh] flex flex-col"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="p-6 border-b border-slate-800 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-mining-teal/10 rounded-lg flex items-center justify-center">
                            <span className="text-mining-teal font-bold text-xl">S</span>
                        </div>
                        <div>
                            <h2 className="text-xl font-semibold text-white">SYNAPSE</h2>
                            <p className="text-xs text-slate-400">Version Information</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* Sprint Info */}
                    <div className="space-y-2">
                        <div className="bg-mining-teal/10 border border-mining-teal/30 rounded-lg p-3">
                            <div className="flex items-center gap-2 mb-1">
                                <div className="w-2 h-2 bg-mining-teal rounded-full"></div>
                                <span className="text-white font-medium text-sm">Current Sprint</span>
                            </div>
                            <p className="text-mining-teal text-sm ml-4">v0.2.2 - UX Professional</p>
                        </div>
                        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-3">
                            <div className="flex items-center gap-2 mb-1">
                                <div className="w-2 h-2 bg-slate-500 rounded-full"></div>
                                <span className="text-slate-300 font-medium text-sm">Next Sprint</span>
                            </div>
                            <p className="text-slate-400 text-sm ml-4">v0.2.3 - 3-Tier Asset Model</p>
                        </div>
                    </div>

                    {/* System Info */}
                    <div className="space-y-3">
                        <h3 className="text-sm font-semibold text-mining-teal uppercase tracking-wider">
                            System
                        </h3>
                        <div className="bg-slate-800/50 rounded-lg p-4 space-y-2 font-mono text-sm">
                            <div className="flex justify-between">
                                <span className="text-slate-400">Platform:</span>
                                <span className="text-white">Web Application</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-slate-400">Framework:</span>
                                <span className="text-white">React 19 + FastAPI</span>
                            </div>
                        </div>
                    </div>
                </div>

            {/* Footer */}
            <div className="p-4 border-t border-slate-800 bg-slate-900/50 flex items-center justify-between gap-3">
                <button
                    onClick={handleCopy}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors text-sm font-medium"
                >
                    {copied ? (
                        <>
                            <Check size={16} className="text-mining-teal" />
                            <span>Copied!</span>
                        </>
                    ) : (
                        <>
                            <Copy size={16} />
                            <span>Copy Version Info</span>
                        </>
                    )}
                </button>
                <a
                    href="https://github.com/yourusername/synapse/blob/main/CHANGELOG.md"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-mining-teal/10 hover:bg-mining-teal/20 text-mining-teal rounded-lg transition-colors text-sm font-medium"
                >
                    <ExternalLink size={16} />
                    <span>Changelog</span>
                </a>
            </div>
            </div>
        </div>
    );
}
