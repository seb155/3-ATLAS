import React, { useState, useRef, useEffect } from 'react';
import apiClient from '../../../services/apiClient';
import { Upload, X, CheckCircle2, AlertCircle, FileText, ArrowRight, ArrowLeft } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Spinner } from '@/components/ui/loading';
import { showToast } from '@/components/ui/toast';
import { useAuthStore } from '@/store/useAuthStore';

interface ImportSummary {
    created: number;
    updated: number;
    errors: string[];
    rules_executed?: number;
    child_assets_created?: number;
    rule_execution_time_ms?: number;
    rule_execution_error?: string;
}

const SYSTEM_FIELDS = [
    { key: 'tag', label: 'Tag', required: true },
    { key: 'type', label: 'Type', required: true },
    { key: 'description', label: 'Description', required: false },
    { key: 'area', label: 'Area', required: false },
    { key: 'system', label: 'System', required: false },
    { key: 'manufacturer_part_id', label: 'Manufacturer Part ID', required: false },
    { key: 'location_id', label: 'Location ID', required: false },
    { key: 'electrical.voltage', label: 'Voltage', required: false },
    { key: 'process.fluid', label: 'Fluid', required: false },
];

export const CSVImportPanel = () => {
    const [file, setFile] = useState<File | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [summary, setSummary] = useState<ImportSummary | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Mapping State
    const [stage, setStage] = useState<'upload' | 'mapping' | 'processing'>('upload');
    const [csvHeaders, setCsvHeaders] = useState<string[]>([]);
    const [mapping, setMapping] = useState<Record<string, string>>({});

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile && droppedFile.name.endsWith('.csv')) {
            processFile(droppedFile);
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            processFile(selectedFile);
        }
    };

    const processFile = (selectedFile: File) => {
        setFile(selectedFile);
        setSummary(null);

        // Parse headers
        const reader = new FileReader();
        reader.onload = (e) => {
            const text = e.target?.result as string;
            const firstLine = text.split('\n')[0];
            if (firstLine) {
                // Simple CSV split (handling quotes roughly)
                // For robust parsing we might need a library, but this works for simple headers
                const headers = firstLine.split(',').map(h => h.trim().replace(/^"|"$/g, ''));
                setCsvHeaders(headers);

                // Auto-map known fields
                const newMapping: Record<string, string> = {};
                SYSTEM_FIELDS.forEach(field => {
                    // Exact match
                    if (headers.includes(field.key)) {
                        newMapping[field.key] = field.key;
                    }
                    // Case-insensitive match
                    else {
                        const match = headers.find(h => h.toLowerCase() === field.key.toLowerCase());
                        if (match) newMapping[field.key] = match;

                        // Label match (e.g. "Tag" -> "tag")
                        const labelMatch = headers.find(h => h.toLowerCase() === field.label.toLowerCase());
                        if (labelMatch) newMapping[field.key] = labelMatch;
                    }
                });
                setMapping(newMapping);
                setStage('mapping');
            }
        };
        reader.readAsText(selectedFile);
    };

    const handleMappingChange = (systemKey: string, csvHeader: string) => {
        setMapping(prev => ({
            ...prev,
            [systemKey]: csvHeader
        }));
    };

    const handleUpload = async () => {
        if (!file) return;

        setIsUploading(true);
        setSummary(null);

        const currentToken = useAuthStore.getState().token;

        if (!currentToken) {
            showToast.error("Authentication Error: No token found. Please login again.");
            setIsUploading(false);
            return;
        }

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('mapping', JSON.stringify(mapping));

            // apiClient handles Base URL and Auth headers automatically
            const response = await apiClient.post('/import_export/import', formData);

            const result = response.data;
            setSummary(result);
            setStage('processing'); // Stay in processing/result view

            // Show success toast
            if (result.errors && result.errors.length > 0) {
                showToast.error(`Import completed with ${result.errors.length} error(s)`);
            } else {
                showToast.success(`Successfully imported ${result.created} asset(s)`);
            }
        } catch (error: any) {
            console.error('Upload error:', error);
            const errorMessage = error.response?.data?.detail || error.message || 'Upload failed';

            setSummary({
                created: 0,
                updated: 0,
                errors: [errorMessage],
            });
            showToast.error(errorMessage);
        } finally {
            setIsUploading(false);
        }
    };

    const handleClear = () => {
        setFile(null);
        setSummary(null);
        setStage('upload');
        setMapping({});
        setCsvHeaders([]);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    return (
        <div className="h-full flex flex-col bg-[#1e1e1e] p-6">
            {/* Header */}
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-white mb-2">Import CSV</h1>
                <p className="text-sm text-[#8b949e]">
                    Upload a CSV file to import assets into the system. Map your columns to the system fields.
                </p>
            </div>

            {/* Content Area */}
            <div className="flex-1 flex flex-col gap-4">

                {/* Stage 1: Upload */}
                {stage === 'upload' && (
                    <div
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                        className={cn(
                            "border-2 border-dashed rounded-lg p-12 flex flex-col items-center justify-center transition-colors cursor-pointer flex-1",
                            isDragging
                                ? "border-[#007fd4] bg-[#007fd4]/10"
                                : "border-[#3e3e42] hover:border-[#007fd4]/50"
                        )}
                        onClick={() => fileInputRef.current?.click()}
                    >
                        <Upload size={48} className={cn(
                            "mb-4",
                            isDragging ? "text-[#007fd4]" : "text-[#858585]"
                        )} />
                        <p className="text-white mb-2">
                            Drop your CSV file here or click to browse
                        </p>
                        <p className="text-sm text-[#8b949e]">
                            Supports .csv files only
                        </p>
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".csv"
                            onChange={handleFileSelect}
                            className="hidden"
                        />
                    </div>
                )}

                {/* Stage 2: Mapping */}
                {stage === 'mapping' && file && (
                    <div className="flex flex-col gap-4 flex-1 overflow-hidden">
                        <div className="flex items-center justify-between bg-[#252526] p-4 rounded-lg border border-[#3e3e42]">
                            <div className="flex items-center gap-3">
                                <FileText className="text-[#007fd4]" />
                                <div>
                                    <p className="text-white font-medium">{file.name}</p>
                                    <p className="text-xs text-[#8b949e]">{csvHeaders.length} columns detected</p>
                                </div>
                            </div>
                            <button
                                onClick={handleClear}
                                className="text-[#8b949e] hover:text-white transition-colors"
                            >
                                <X size={20} />
                            </button>
                        </div>

                        <div className="flex-1 overflow-y-auto border border-[#3e3e42] rounded-lg bg-[#1e1e1e] p-4">
                            <h3 className="text-white font-bold mb-4">Map Columns</h3>
                            <div className="grid grid-cols-[1fr,auto,1fr] gap-4 items-center mb-2 px-2 text-sm text-[#8b949e] font-medium">
                                <div>System Field</div>
                                <div></div>
                                <div>CSV Header</div>
                            </div>

                            <div className="space-y-2">
                                {SYSTEM_FIELDS.map((field) => (
                                    <div key={field.key} className="grid grid-cols-[1fr,auto,1fr] gap-4 items-center bg-[#252526] p-3 rounded border border-[#3e3e42]">
                                        <div className="flex flex-col">
                                            <span className="text-white font-medium">
                                                {field.label}
                                                {field.required && <span className="text-red-500 ml-1">*</span>}
                                            </span>
                                            <span className="text-xs text-[#8b949e] font-mono">{field.key}</span>
                                        </div>

                                        <ArrowRight size={16} className="text-[#8b949e]" />

                                        <select
                                            value={mapping[field.key] || ''}
                                            onChange={(e) => handleMappingChange(field.key, e.target.value)}
                                            className="bg-[#3e3e42] text-white border border-[#555] rounded px-3 py-2 text-sm focus:outline-none focus:border-[#007fd4]"
                                        >
                                            <option value="">-- Select Column --</option>
                                            {csvHeaders.map(header => (
                                                <option key={header} value={header}>{header}</option>
                                            ))}
                                        </select>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="flex gap-3 mt-2">
                            <button
                                onClick={handleClear}
                                className="px-4 py-2 rounded bg-[#3e3e42] text-white font-medium hover:bg-[#4e4e52] transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleUpload}
                                disabled={isUploading}
                                className={cn(
                                    "flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded bg-[#007fd4] text-white font-medium transition-colors",
                                    isUploading
                                        ? "opacity-50 cursor-not-allowed"
                                        : "hover:bg-[#0069b4]"
                                )}
                            >
                                {isUploading ? (
                                    <>
                                        <Spinner size="small" />
                                        Importing...
                                    </>
                                ) : (
                                    <>
                                        <Upload size={16} />
                                        Start Import
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                )}

                {/* Stage 3: Results (Summary) */}
                {stage === 'processing' && summary && (
                    <div className="flex flex-col gap-4 flex-1">
                        <div className="border border-[#3e3e42] rounded-lg p-6 bg-[#252526]">
                            <h2 className="text-lg font-bold text-white mb-4">Import Summary</h2>

                            <div className="space-y-3">
                                {/* Success Stats */}
                                <div className="flex items-center gap-3 text-sm">
                                    <CheckCircle2 size={16} className="text-green-500" />
                                    <span className="text-[#cccccc]">
                                        <strong className="text-white">{summary.created}</strong> assets created
                                    </span>
                                </div>
                                <div className="flex items-center gap-3 text-sm">
                                    <CheckCircle2 size={16} className="text-blue-500" />
                                    <span className="text-[#cccccc]">
                                        <strong className="text-white">{summary.updated}</strong> assets updated
                                    </span>
                                </div>

                                {/* Rule Execution Stats */}
                                {summary.rules_executed !== undefined && (
                                    <>
                                        <div className="flex items-center gap-3 text-sm">
                                            <FileText size={16} className="text-purple-500" />
                                            <span className="text-[#cccccc]">
                                                <strong className="text-white">{summary.rules_executed}</strong> rules executed
                                            </span>
                                        </div>
                                        {summary.child_assets_created !== undefined && (
                                            <div className="flex items-center gap-3 text-sm">
                                                <CheckCircle2 size={16} className="text-purple-500" />
                                                <span className="text-[#cccccc]">
                                                    <strong className="text-white">{summary.child_assets_created}</strong> child assets created
                                                </span>
                                            </div>
                                        )}
                                        {summary.rule_execution_time_ms !== undefined && (
                                            <div className="flex items-center gap-3 text-sm text-[#8b949e]">
                                                <span>Execution time: {summary.rule_execution_time_ms}ms</span>
                                            </div>
                                        )}
                                    </>
                                )}

                                {/* Errors */}
                                {summary.errors.length > 0 && (
                                    <div className="mt-4 pt-4 border-t border-[#3e3e42]">
                                        <div className="flex items-center gap-2 mb-2">
                                            <AlertCircle size={16} className="text-red-500" />
                                            <span className="text-white font-medium">
                                                {summary.errors.length} error{summary.errors.length !== 1 ? 's' : ''}
                                            </span>
                                        </div>
                                        <div className="max-h-[200px] overflow-y-auto">
                                            {summary.errors.map((error, idx) => (
                                                <div key={idx} className="text-sm text-red-400 mb-1 font-mono">
                                                    {error}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Rule Execution Error */}
                                {summary.rule_execution_error && (
                                    <div className="mt-4 pt-4 border-t border-[#3e3e42]">
                                        <div className="flex items-center gap-2 mb-2">
                                            <AlertCircle size={16} className="text-yellow-500" />
                                            <span className="text-white font-medium">Rule Execution Warning</span>
                                        </div>
                                        <div className="text-sm text-yellow-400">
                                            {summary.rule_execution_error}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="flex justify-end">
                            <button
                                onClick={handleClear}
                                className="flex items-center gap-2 px-4 py-2 rounded bg-[#3e3e42] text-white font-medium hover:bg-[#4e4e52] transition-colors"
                            >
                                <ArrowLeft size={16} />
                                Import Another File
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
