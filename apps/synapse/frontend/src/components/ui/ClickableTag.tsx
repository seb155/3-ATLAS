import React from 'react';
import { useAssetNavigation } from '../../hooks/useAssetNavigation';

interface ClickableTagProps {
    tag: string;
    assetId: string;
    onClick?: (assetId: string) => void;
    className?: string;
}

export function ClickableTag({ tag, assetId, onClick, className = '' }: ClickableTagProps) {
    const { navigateToAsset } = useAssetNavigation();

    const handleClick = (e: React.MouseEvent) => {
        e.stopPropagation(); // Prevent event bubbling to parent (row click)

        // Navigate using React Router
        navigateToAsset(assetId);

        // Also call original callback if provided
        onClick?.(assetId);
    };

    return (
        <button
            onClick={handleClick}
            className={`font-mono font-medium text-mining-teal hover:underline cursor-pointer transition-all duration-150 hover:scale-105 hover:text-mining-teal/80 inline-block ${className}`}
            title={`Navigate to ${tag}`}
        >
            {tag}
        </button>
    );
}
