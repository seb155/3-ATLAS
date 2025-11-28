import React, { useState, useRef } from 'react';
import {
  Upload,
  FileSpreadsheet,
  AlertCircle,
  CheckCircle,
  Loader2,
  X,
  TrendingUp,
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Alert, AlertDescription } from '../components/ui/Alert';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/Table';
import { Badge } from '../components/ui/Badge';
import apiClient from '../services/apiClient';
import { ImportResponse, ImportError, ImportSummary } from '../types/import.types';
import toast from 'react-hot-toast';

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export default function ModernIngestion() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [summary, setSummary] = useState<ImportSummary | null>(null);
  const [errors, setErrors] = useState<ImportError[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // File validation
  const validateFile = (selectedFile: File): boolean => {
    // Check file type
    if (!selectedFile.name.endsWith('.csv')) {
      toast.error('Only CSV files are allowed');
      return false;
    }

    // Check file size
    if (selectedFile.size > MAX_FILE_SIZE) {
      toast.error(`File size must be less than ${MAX_FILE_SIZE / 1024 / 1024}MB`);
      return false;
    }

    return true;
  };

  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && validateFile(selectedFile)) {
      setFile(selectedFile);
      // Clear previous results
      setSummary(null);
      setErrors([]);
    }
  };

  // Handle drag and drop
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && validateFile(droppedFile)) {
      setFile(droppedFile);
      // Clear previous results
      setSummary(null);
      setErrors([]);
    }
  };

  // Upload CSV file
  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a file first');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await apiClient.post<ImportResponse>('/import_export/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const data = response.data;
      setSummary({
        success: data.success,
        total_rows: data.total_rows,
        created: data.created,
        updated: data.updated,
        failed: data.failed,
        rules_executed: data.rules_executed,
        child_assets_created: data.child_assets_created,
        rule_execution_time_ms: data.rule_execution_time_ms,
      });
      setErrors(data.errors || []);

      if (data.success && data.failed === 0) {
        toast.success(`Successfully imported ${data.created + data.updated} assets!`);
      } else if (data.success && data.failed > 0) {
        toast.success(
          `Imported ${data.created + data.updated} assets with ${data.failed} failures`
        );
      } else {
        toast.error('Import completed with errors');
      }
    } catch (error: unknown) {
      const message =
        (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Failed to upload CSV file';
      toast.error(message);
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  };

  // Clear file and results
  const handleClear = () => {
    setFile(null);
    setSummary(null);
    setErrors([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="p-6 space-y-6 bg-[#1e1e1e] min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <FileSpreadsheet className="text-[#007acc]" />
            CSV Import
          </h1>
          <p className="text-gray-400 mt-1">Upload asset data from CSV files</p>
        </div>
      </div>

      {/* Upload Section */}
      <Card className="bg-[#252526] border-[#3e3e42]">
        <CardHeader>
          <CardTitle className="text-white">Upload CSV File</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Drag & Drop Zone */}
          <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center transition-colors
              ${dragActive ? 'border-[#007acc] bg-[#007acc]/10' : 'border-[#3e3e42] hover:border-[#555555]'}
            `}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="hidden"
              id="csv-upload"
            />

            {!file ? (
              <div className="space-y-4">
                <div className="flex justify-center">
                  <Upload className="h-12 w-12 text-gray-400" />
                </div>
                <div>
                  <p className="text-gray-300 mb-2">Drag and drop your CSV file here, or</p>
                  <label htmlFor="csv-upload">
                    <Button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="bg-[#007acc] hover:bg-[#005a9e] text-white"
                    >
                      Choose File
                    </Button>
                  </label>
                </div>
                <p className="text-sm text-gray-500">Supported: CSV files up to 10MB</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-center gap-3 text-gray-300">
                  <FileSpreadsheet className="h-8 w-8 text-[#007acc]" />
                  <div className="text-left">
                    <p className="font-medium">{file.name}</p>
                    <p className="text-sm text-gray-400">{formatFileSize(file.size)}</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleClear}
                    className="text-gray-400 hover:text-white"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
                <div className="flex gap-2 justify-center">
                  <Button
                    onClick={handleUpload}
                    disabled={uploading}
                    className="bg-[#007acc] hover:bg-[#005a9e] text-white"
                  >
                    {uploading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload className="mr-2 h-4 w-4" />
                        Upload CSV
                      </>
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleClear}
                    disabled={uploading}
                    className="border-[#3e3e42] text-gray-300 hover:bg-[#333333]"
                  >
                    Clear
                  </Button>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Success Alert */}
      {summary && summary.success && (
        <Alert variant="success" className="border-green-900 bg-green-900/20">
          <CheckCircle className="h-4 w-4" />
          <AlertDescription className="text-green-400">
            Import completed successfully!
          </AlertDescription>
        </Alert>
      )}

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-[#252526] border-[#3e3e42]">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Total Rows</p>
                  <p className="text-2xl font-bold text-blue-400">{summary.total_rows}</p>
                </div>
                <FileSpreadsheet className="h-8 w-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-[#252526] border-[#3e3e42]">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Created</p>
                  <p className="text-2xl font-bold text-green-400">{summary.created}</p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-[#252526] border-[#3e3e42]">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Updated</p>
                  <p className="text-2xl font-bold text-yellow-400">{summary.updated}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-yellow-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-[#252526] border-[#3e3e42]">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Failed</p>
                  <p className="text-2xl font-bold text-red-400">{summary.failed}</p>
                </div>
                <AlertCircle className="h-8 w-8 text-red-400" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Rule Execution Stats */}
      {summary && (summary.rules_executed || summary.child_assets_created) && (
        <Card className="bg-[#252526] border-[#3e3e42]">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-[#007acc]" />
              Rule Execution Statistics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {summary.rules_executed !== undefined && (
                <div>
                  <p className="text-sm text-gray-400">Rules Executed</p>
                  <p className="text-xl font-bold text-white">{summary.rules_executed}</p>
                </div>
              )}
              {summary.child_assets_created !== undefined && (
                <div>
                  <p className="text-sm text-gray-400">Child Assets Created</p>
                  <p className="text-xl font-bold text-white">{summary.child_assets_created}</p>
                </div>
              )}
              {summary.rule_execution_time_ms !== undefined && (
                <div>
                  <p className="text-sm text-gray-400">Execution Time</p>
                  <p className="text-xl font-bold text-white">
                    {summary.rule_execution_time_ms.toFixed(2)} ms
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Errors Table */}
      {errors.length > 0 && (
        <Card className="bg-[#252526] border-[#3e3e42]">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-400" />
              Import Errors ({errors.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="max-h-96 overflow-y-auto">
              <Table>
                <TableHeader>
                  <TableRow className="border-[#3e3e42] hover:bg-[#333333]">
                    <TableHead className="text-gray-400">Row #</TableHead>
                    <TableHead className="text-gray-400">Tag</TableHead>
                    <TableHead className="text-gray-400">Error Message</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {errors.map((error, index) => (
                    <TableRow key={index} className="border-[#3e3e42] hover:bg-red-900/10">
                      <TableCell className="text-white font-mono">
                        <Badge variant="destructive">{error.row}</Badge>
                      </TableCell>
                      <TableCell className="text-gray-300 font-mono">
                        {error.tag || <span className="italic text-gray-500">N/A</span>}
                      </TableCell>
                      <TableCell className="text-red-400">{error.error}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Empty State - No Results */}
      {!summary && !file && (
        <Card className="bg-[#252526] border-[#3e3e42]">
          <CardContent className="p-12 text-center">
            <FileSpreadsheet className="h-16 w-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 text-lg">No file uploaded yet</p>
            <p className="text-gray-500 text-sm mt-2">
              Upload a CSV file to import asset data into the system
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
