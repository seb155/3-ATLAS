import React from 'react';

// Spinner Component
interface SpinnerProps {
    size?: 'small' | 'medium' | 'large';
    className?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({ size = 'medium', className = '' }) => {
    const sizeClasses = {
        small: 'w-4 h-4 border-2',
        medium: 'w-8 h-8 border-2',
        large: 'w-12 h-12 border-3'
    };

    return (
        <div
            className={`${sizeClasses[size]} border-mining-teal border-t-transparent rounded-full animate-spin ${className}`}
            role="status"
            aria-label="Loading"
        />
    );
};

// Skeleton Loader
interface SkeletonProps {
    width?: string;
    height?: string;
    className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({
    width = 'w-full',
    height = 'h-4',
    className = ''
}) => {
    return (
        <div
            className={`${width} ${height} bg-slate-800 rounded animate-pulse ${className}`}
            role="status"
            aria-label="Loading content"
        />
    );
};

// Loading Overlay (for full-page loading)
interface LoadingOverlayProps {
    message?: string;
    show: boolean;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ message = 'Loading...', show }) => {
    if (!show) return null;

    return (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-8 flex flex-col items-center gap-4 shadow-xl">
                <Spinner size="large" />
                <p className="text-slate-300 text-sm font-medium">{message}</p>
            </div>
        </div>
    );
};

// Progress Bar
interface ProgressBarProps {
    progress: number; // 0-100
    className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ progress, className = '' }) => {
    return (
        <div className={`w-full bg-slate-800 rounded-full h-2 overflow-hidden ${className}`}>
            <div
                className="bg-mining-teal h-full transition-all duration-300 ease-out"
                style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
                role="progressbar"
                aria-valuenow={progress}
                aria-valuemin={0}
                aria-valuemax={100}
            />
        </div>
    );
};

// Card Skeleton
export const CardSkeleton: React.FC = () => {
    return (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 space-y-3">
            <Skeleton height="h-6" width="w-3/4" />
            <Skeleton height="h-4" width="w-full" />
            <Skeleton height="h-4" width="w-5/6" />
        </div>
    );
};

// List Skeleton
interface ListSkeletonProps {
    rows?: number;
}

export const ListSkeleton: React.FC<ListSkeletonProps> = ({ rows = 5 }) => {
    return (
        <div className="space-y-2">
            {Array.from({ length: rows }).map((_, i) => (
                <div key={i} className="flex items-center gap-3 p-2">
                    <Skeleton width="w-8" height="h-8" className="rounded-full" />
                    <div className="flex-1 space-y-2">
                        <Skeleton width="w-1/3" height="h-3" />
                        <Skeleton width="w-1/2" height="h-3" />
                    </div>
                </div>
            ))}
        </div>
    );
};
