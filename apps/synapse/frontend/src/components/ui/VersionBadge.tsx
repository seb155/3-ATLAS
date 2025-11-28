import { useState } from 'react';
import { Info } from 'lucide-react';
import { VERSION } from '../config/version';

interface VersionBadgeProps {
    onClick?: () => void;
}

export function VersionBadge({ onClick }: VersionBadgeProps) {
    const [isHovered, setIsHovered] = useState(false);

    return (
        <button
            onClick={onClick}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            className="w-full flex items-center justify-between p-2 text-xs font-mono rounded transition-colors hover:bg-slate-800/50 group"
            title="Click for version details"
        >
            <div className="flex flex-col items-start">
                <span className="text-slate-500">SYNAPSE</span>
                <span className="text-mining-teal font-semibold">
                    v{VERSION.app}
                    <span className="text-slate-600 ml-1">#{VERSION.buildNumber.slice(-6)}</span>
                </span>
            </div>
            <Info
                size={14}
                className={`transition-all ${isHovered ? 'text-mining-teal' : 'text-slate-600'
                    }`}
            />
        </button>
    );
}
