import { useState } from 'react';
import { Download, FileText } from 'lucide-react';
import { usePackages } from '../../hooks/usePackages';
import { useProjectStore } from '../../store/useProjectStore';

interface ExportDropdownProps {
    packageId: string;
    packageType?: string;
}

export const ExportDropdown: React.FC<ExportDropdownProps> = ({
    packageId,
    packageType
}) => {
    const { currentProject } = useProjectStore();
    const { exportPackage } = usePackages(currentProject?.id || '');
    const [isExporting, setIsExporting] = useState(false);
    const [isOpen, setIsOpen] = useState(false);

    const handleExport = async (templateType: 'IN-P040' | 'CA-P040') => {
        setIsExporting(true);
        setIsOpen(false);
        try {
            const success = await exportPackage(packageId, templateType, 'xlsx');
            if (success) {
                console.log('Export successful');
                // TODO: Add toast notification
            } else {
                console.error('Export failed');
                // TODO: Add error toast
            }
        } catch (error) {
            console.error('Export failed:', error);
            // TODO: Add error toast
        } finally {
            setIsExporting(false);
        }
    };

    return (
        <div className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                disabled={isExporting}
                className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-white text-sm rounded border border-slate-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
                <Download size={14} />
                {isExporting ? 'Exporting...' : 'Export'}
            </button>

            {isOpen && (
                <>
                    {/* Backdrop */}
                    <div
                        className="fixed inset-0 z-10"
                        onClick={() => setIsOpen(false)}
                    />

                    {/* Dropdown Menu */}
                    <div className="absolute right-0 mt-2 w-64 bg-slate-800 border border-slate-700 rounded shadow-lg z-20">
                        <div className="p-2">
                            <button
                                onClick={() => handleExport('IN-P040')}
                                className="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-200 hover:bg-slate-700 rounded transition-colors"
                            >
                                <FileText size={14} className="text-mining-teal" />
                                <div className="flex-1 text-left">
                                    <div className="font-medium">IN-P040</div>
                                    <div className="text-xs text-slate-400">Instrument Index</div>
                                </div>
                            </button>

                            <button
                                onClick={() => handleExport('CA-P040')}
                                className="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-200 hover:bg-slate-700 rounded transition-colors"
                            >
                                <FileText size={14} className="text-mining-gold" />
                                <div className="flex-1 text-left">
                                    <div className="font-medium">CA-P040</div>
                                    <div className="text-xs text-slate-400">Cable Schedule</div>
                                </div>
                            </button>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};
