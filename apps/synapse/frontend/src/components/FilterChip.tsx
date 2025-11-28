import React from 'react';

interface FilterChipProps {
    label: string;
    active: boolean;
    onClick: () => void;
    variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
}

const VARIANT_STYLES = {
    default: 'bg-slate-700 text-slate-300 hover:bg-slate-600',
    primary: 'bg-blue-600 text-white hover:bg-blue-500',
    success: 'bg-green-600 text-white hover:bg-green-500',
    warning: 'bg-yellow-600 text-white hover:bg-yellow-500',
    danger: 'bg-red-600 text-white hover:bg-red-500',
};

export function FilterChip({ label, active, onClick, variant = 'default' }: FilterChipProps) {
    const baseStyles = 'px-2 py-0.5 rounded text-[10px] font-medium border transition-colors cursor-pointer select-none';
    const activeStyles = active
        ? `${VARIANT_STYLES[variant]} border-slate-600 shadow-sm`
        : 'bg-transparent text-slate-500 border-slate-700 hover:bg-slate-800 hover:text-slate-300';

    return (
        <button
            onClick={onClick}
            className={`${baseStyles} ${activeStyles}`}
            title={`Toggle ${label}`}
        >
            {label}
        </button>
    );
}
