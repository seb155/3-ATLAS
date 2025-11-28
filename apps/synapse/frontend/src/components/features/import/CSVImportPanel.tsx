import React, { useState, useRef } from 'react';
import apiClient from '../../../services/apiClient';


interface ImportSummary {
    created: number;
    updated: number;
    errors: string[];
    rules_executed?: number;
    child_assets_created?: number;
    rule_execution_time_ms?: number;
    rule_execution_error?: string;
}

export const CSVImportPanel = () => {
    const [file, setFile] = useState<File | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [summary, setSummary] = useState<ImportSummary | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);



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
            setFile(droppedFile);
            setSummary(null);
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            setFile(selectedFile);
            setSummary(null);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setIsUploading(true);
        setSummary(null);

        const currentToken = useAuthStore.getState().token;
        console.log(' [CSV] Starting upload via apiClient...', 'File:', file.name, 'Token available:', !!currentToken);

        if (!currentToken) {
            showToast.error("Authentication Error: No token found. Please login again.");
            setIsUploading(false);
            return;
        }

        try {
            const formData = new FormData();
            formData.append('file', file);

            // apiClient handles Base URL and Auth headers automatically
            const response = await apiClient.post('/import_export/import', formData);

            const result = response.data;
            setSummary(result);

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
                    Upload a CSV file to import assets into the system. The file will be validated and assets will be created or updated accordingly.
                </p>
            </div>

            {/* Upload Area */}
            <div className="flex-1 flex flex-col gap-4">
                {/* Drag & Drop Zone */}
                <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={cn(
                        "border-2 border-dashed rounded-lg p-12 flex flex-col items-center justify-center transition-colors cursor-pointer",
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
                        {file ? file.name : 'Drop your CSV file here or click to browse'}
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

                {/* Actions */}
                {file && (
                    <div className="flex gap-3">
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
                                    Uploading...
                                </>
                            ) : (
                                <>
                                    <Upload size={16} />
                                    Upload & Import
                                </>
                            )}
                        </button>
                        <button
                            onClick={handleClear}
                            disabled={isUploading}
                            className="px-4 py-2 rounded bg-[#3e3e42] text-white font-medium hover:bg-[#4e4e52] transition-colors disabled:opacity-50"
                        >
                            <X size={16} />
                        </button>
                    </div>
                )}

                {/* Summary */}
                {summary && (
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
                )}

                {/* TODO: Re-enable when backend export endpoint is implemented
                <div className="mt-auto pt-4 border-t border-[#3e3e42]">
                    <button
                        onClick={() => window.open('http://localhost:8001/api/v1/import_export/export', '_blank')}
                        className="flex items-center gap-2 text-[#007fd4] hover:text-[#0069b4] transition-colors text-sm"
                    >
                        <Download size={16} />
                        Download CSV Template
                    </button>
                </div>
                */}
            </div>
        </div>
    );
};
