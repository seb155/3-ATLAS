import React from 'react';
import { AppLayout } from '../components/layout/AppLayout';
import { CSVImportPanel } from '../components/features/import/CSVImportPanel';
import { ErrorBoundary } from '../components/ErrorBoundary';
import { ToastProvider } from '../components/ui/toast';

const AppShellContent = () => {
    const [activeView, setActiveView] = React.useState('welcome');

    const renderContent = () => {
        switch (activeView) {
            case 'import':
                return <CSVImportPanel />;
            case 'explorer':
                return (
                    <div className="p-8">
                        <h1 className="text-2xl font-bold text-white mb-4">Explorer</h1>
                        <p className="text-slate-400">Navigate your project assets and files.</p>
                    </div>
                );
            case 'search':
                return (
                    <div className="p-8">
                        <h1 className="text-2xl font-bold text-white mb-4">Search</h1>
                        <p className="text-slate-400">Global search across all data.</p>
                    </div>
                );
            default:
                return (
                    <div className="p-8">
                        <h1 className="text-2xl font-bold text-white mb-4">Welcome to SYNAPSE</h1>
                        <p className="text-slate-400">
                            Engineering data management and automation platform.
                        </p>
                        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="p-4 bg-[#252526] border border-[#333333] rounded">
                                <h2 className="font-bold text-[#007fd4] mb-2">Explorer</h2>
                                <p className="text-sm">Navigate your project assets and files.</p>
                            </div>
                            <div className="p-4 bg-[#252526] border border-[#333333] rounded">
                                <h2 className="font-bold text-[#007fd4] mb-2">Search</h2>
                                <p className="text-sm">Global search across all data.</p>
                            </div>
                        </div>
                    </div>
                );
        }
    };

    return (
        <AppLayout onActivityChange={setActiveView}>
            {renderContent()}
        </AppLayout>
    );
};

export const AppShell = () => {
    return (
        <ErrorBoundary>
            <ToastProvider />
            <AppShellContent />
        </ErrorBoundary>
    );
};

