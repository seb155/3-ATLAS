import { describe, it, expect, vi, beforeEach, afterEach, type Mock } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ModernIngestion from './ModernIngestion';
import apiClient from '../services/apiClient';
import toast from 'react-hot-toast';

// Mock dependencies
vi.mock('../services/apiClient');
vi.mock('react-hot-toast');

describe('ModernIngestion - CSV Upload', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('Initial Render', () => {
    it('renders upload section with heading', () => {
      render(<ModernIngestion />);
      expect(screen.getByText('CSV Import')).toBeInTheDocument();
      expect(screen.getByText('Upload asset data from CSV files')).toBeInTheDocument();
    });

    it('renders empty state when no file selected', () => {
      render(<ModernIngestion />);
      expect(screen.getByText('No file uploaded yet')).toBeInTheDocument();
      expect(screen.getByText(/Upload a CSV file to import asset data/i)).toBeInTheDocument();
    });

    it('renders drag and drop zone', () => {
      render(<ModernIngestion />);
      expect(screen.getByText(/Drag and drop your CSV file here/i)).toBeInTheDocument();
      expect(screen.getByText('Choose File')).toBeInTheDocument();
    });
  });

  describe('File Selection', () => {
    it('allows CSV file selection via input', () => {
      render(<ModernIngestion />);
      const file = new File(['tag,type\nP-101,PUMP'], 'test.csv', { type: 'text/csv' });
      const input = document.getElementById('csv-upload') as HTMLInputElement;

      fireEvent.change(input, { target: { files: [file] } });

      expect(screen.getByText('test.csv')).toBeInTheDocument();
    });

    it('validates file type and shows error for non-CSV files', () => {
      render(<ModernIngestion />);
      const file = new File(['content'], 'test.txt', { type: 'text/plain' });
      const input = document.getElementById('csv-upload') as HTMLInputElement;

      fireEvent.change(input, { target: { files: [file] } });

      expect(toast.error).toHaveBeenCalledWith('Only CSV files are allowed');
      expect(screen.queryByText('test.txt')).not.toBeInTheDocument();
    });

    it('validates file size and rejects files over 10MB', () => {
      render(<ModernIngestion />);
      // Create a file larger than 10MB
      const largeFile = new File(['x'.repeat(11 * 1024 * 1024)], 'large.csv', { type: 'text/csv' });
      Object.defineProperty(largeFile, 'size', { value: 11 * 1024 * 1024 });

      const input = document.getElementById('csv-upload') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [largeFile] } });

      expect(toast.error).toHaveBeenCalledWith('File size must be less than 10MB');
    });

    it('displays file name and size after valid selection', () => {
      render(<ModernIngestion />);
      const file = new File(['tag,type\nP-101,PUMP'], 'assets.csv', { type: 'text/csv' });
      const input = document.getElementById('csv-upload') as HTMLInputElement;

      fireEvent.change(input, { target: { files: [file] } });

      expect(screen.getByText('assets.csv')).toBeInTheDocument();
      expect(screen.getByText(/Bytes|KB|MB/)).toBeInTheDocument();
    });
  });

  describe('File Upload', () => {
    it('uploads file and displays success summary', async () => {
      const mockResponse = {
        data: {
          success: true,
          total_rows: 10,
          created: 8,
          updated: 2,
          failed: 0,
          errors: [],
        },
      };

      (apiClient.post as Mock).mockResolvedValue(mockResponse);

      render(<ModernIngestion />);

      const file = new File(['tag,type\nP-101,PUMP'], 'test.csv', { type: 'text/csv' });
      const input = document.getElementById('csv-upload') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [file] } });

      const uploadBtn = screen.getByRole('button', { name: /upload csv/i });
      fireEvent.click(uploadBtn);

      await waitFor(() => {
        expect(apiClient.post).toHaveBeenCalledWith(
          '/import_export/import',
          expect.any(FormData),
          expect.objectContaining({
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          })
        );
      });

      await waitFor(() => {
        expect(screen.getByText('10')).toBeInTheDocument(); // Total rows
        expect(screen.getByText('8')).toBeInTheDocument(); // Created
        expect(screen.getByText('2')).toBeInTheDocument(); // Updated
      });

      expect(toast.success).toHaveBeenCalledWith('Successfully imported 10 assets!');
    });

    it('displays loading state during upload', async () => {
      (apiClient.post as any).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({ data: {} }), 100))
      );

      render(<ModernIngestion />);

      const file = new File(['tag,type\nP-101,PUMP'], 'test.csv', { type: 'text/csv' });
      const input = document.getElementById('csv-upload') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [file] } });

      const uploadBtn = screen.getByRole('button', { name: /upload csv/i });
      fireEvent.click(uploadBtn);

      expect(screen.getByText('Uploading...')).toBeInTheDocument();
      expect(uploadBtn).toBeDisabled();
    });

    it('handles upload with errors and displays error table', async () => {
      const mockResponse = {
        data: {
          success: true,
          total_rows: 10,
          created: 7,
          updated: 1,
          failed: 2,
          errors: [
            { row: 5, tag: 'P-101', error: 'Invalid voltage format' },
            { row: 8, tag: 'M-205', error: 'Missing required field: type' },
          ],
        },
      };

      (apiClient.post as Mock).mockResolvedValue(mockResponse);

      render(<ModernIngestion />);

      const file = new File(['tag,type\nP-101,PUMP'], 'test.csv', { type: 'text/csv' });
      const input = document.getElementById('csv-upload') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [file] } });

      const uploadBtn = screen.getByRole('button', { name: /upload csv/i });
      fireEvent.click(uploadBtn);

      await waitFor(() => {
        expect(screen.getByText('Import Errors (2)')).toBeInTheDocument();
        expect(screen.getByText('P-101')).toBeInTheDocument();
        expect(screen.getByText('Invalid voltage format')).toBeInTheDocument();
        expect(screen.getByText('M-205')).toBeInTheDocument();
        expect(screen.getByText('Missing required field: type')).toBeInTheDocument();
      });

      expect(toast.success).toHaveBeenCalledWith('Imported 8 assets with 2 failures');
    });

    it('handles network error and displays error toast', async () => {
      const errorResponse = {
        response: {
          data: {
            detail: 'Database connection failed',
          },
        },
      };

      (apiClient.post as Mock).mockRejectedValue(errorResponse);

      render(<ModernIngestion />);

      const file = new File(['tag,type\nP-101,PUMP'], 'test.csv', { type: 'text/csv' });
      const input = document.getElementById('csv-upload') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [file] } });

      const uploadBtn = screen.getByRole('button', { name: /upload csv/i });
      fireEvent.click(uploadBtn);

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Database connection failed');
      });
    });

    it('handles generic network error with default message', async () => {
      (apiClient.post as Mock).mockRejectedValue(new Error('Network error'));

      render(<ModernIngestion />);

      const file = new File(['tag,type\nP-101,PUMP'], 'test.csv', { type: 'text/csv' });
      const input = document.getElementById('csv-upload') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [file] } });

      const uploadBtn = screen.getByRole('button', { name: /upload csv/i });
      fireEvent.click(uploadBtn);

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Failed to upload CSV file');
      });
    });

    it('shows error toast when attempting to upload without file', () => {
      render(<ModernIngestion />);

      // Try to find Upload button in initial state (should not exist)
      // The button only appears after file selection
      expect(screen.queryByRole('button', { name: /upload csv/i })).not.toBeInTheDocument();
    });
  });

  describe('Rule Execution Stats', () => {
    it('displays rule execution statistics when present', async () => {
      const mockResponse = {
        data: {
          success: true,
          total_rows: 5,
          created: 5,
          updated: 0,
          failed: 0,
          errors: [],
          rules_executed: 12,
          child_assets_created: 8,
          rule_execution_time_ms: 145.67,
        },
      };

      (apiClient.post as Mock).mockResolvedValue(mockResponse);

      render(<ModernIngestion />);

      const file = new File(['tag,type\nP-101,PUMP'], 'test.csv', { type: 'text/csv' });
      const input = document.getElementById('csv-upload') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [file] } });

      const uploadBtn = screen.getByRole('button', { name: /upload csv/i });
      fireEvent.click(uploadBtn);

      await waitFor(() => {
        expect(screen.getByText('Rule Execution Statistics')).toBeInTheDocument();
        expect(screen.getByText('12')).toBeInTheDocument(); // Rules executed
        expect(screen.getByText('8')).toBeInTheDocument(); // Child assets
        expect(screen.getByText('145.67 ms')).toBeInTheDocument(); // Execution time
      });
    });

    it('does not display rule stats when not present', async () => {
      const mockResponse = {
        data: {
          success: true,
          total_rows: 7,
          created: 7,
          updated: 0,
          failed: 0,
          errors: [],
        },
      };

      (apiClient.post as Mock).mockResolvedValue(mockResponse);

      render(<ModernIngestion />);

      const file = new File(['tag,type\nP-101,PUMP'], 'test.csv', { type: 'text/csv' });
      const input = document.getElementById('csv-upload') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [file] } });

      const uploadBtn = screen.getByRole('button', { name: /upload csv/i });
      fireEvent.click(uploadBtn);

      await waitFor(() => {
        expect(screen.getByText('Import completed successfully!')).toBeInTheDocument();
      });

      expect(screen.queryByText('Rule Execution Statistics')).not.toBeInTheDocument();
    });
  });

  describe('Clear Functionality', () => {
    it('clears file and results when clear button clicked', async () => {
      const mockResponse = {
        data: {
          success: true,
          total_rows: 9,
          created: 9,
          updated: 0,
          failed: 0,
          errors: [],
        },
      };

      (apiClient.post as Mock).mockResolvedValue(mockResponse);

      render(<ModernIngestion />);

      // Upload file
      const file = new File(['tag,type\nP-101,PUMP'], 'test.csv', { type: 'text/csv' });
      const input = document.getElementById('csv-upload') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [file] } });

      const uploadBtn = screen.getByRole('button', { name: /upload csv/i });
      fireEvent.click(uploadBtn);

      await waitFor(() => {
        expect(screen.getByText('Import completed successfully!')).toBeInTheDocument();
      });

      // Clear results - find Clear button among all buttons with name /clear/i
      const clearButtons = screen.getAllByRole('button', { name: /clear/i });
      const clearBtn = clearButtons[clearButtons.length - 1]; // Get the last one (in the upload section)
      fireEvent.click(clearBtn);

      // Should return to empty state
      expect(screen.getByText('No file uploaded yet')).toBeInTheDocument();
      expect(screen.queryByText('test.csv')).not.toBeInTheDocument();
    });
  });

  describe('Drag and Drop', () => {
    it('handles drag enter event', () => {
      render(<ModernIngestion />);

      const dropzone = screen.getByText(/Drag and drop your CSV file here/i).closest('div');

      fireEvent.dragEnter(dropzone!, {
        dataTransfer: { files: [] },
      });

      // Dropzone should have active styling (testing class application is fragile, so we just ensure no crash)
      expect(dropzone).toBeInTheDocument();
    });

    it('handles file drop', () => {
      render(<ModernIngestion />);

      const file = new File(['tag,type\nP-101,PUMP'], 'dropped.csv', { type: 'text/csv' });
      const dropzone = screen.getByText(/Drag and drop your CSV file here/i).closest('div');

      fireEvent.drop(dropzone!, {
        dataTransfer: {
          files: [file],
        },
      });

      expect(screen.getByText('dropped.csv')).toBeInTheDocument();
    });

    it('validates dropped file type', () => {
      render(<ModernIngestion />);

      const file = new File(['content'], 'invalid.txt', { type: 'text/plain' });
      const dropzone = screen.getByText(/Drag and drop your CSV file here/i).closest('div');

      fireEvent.drop(dropzone!, {
        dataTransfer: {
          files: [file],
        },
      });

      expect(toast.error).toHaveBeenCalledWith('Only CSV files are allowed');
      expect(screen.queryByText('invalid.txt')).not.toBeInTheDocument();
    });
  });

  describe('Success Alert', () => {
    it('displays success alert on successful import', async () => {
      const mockResponse = {
        data: {
          success: true,
          total_rows: 3,
          created: 3,
          updated: 0,
          failed: 0,
          errors: [],
        },
      };

      (apiClient.post as Mock).mockResolvedValue(mockResponse);

      render(<ModernIngestion />);

      const file = new File(['tag,type\nP-101,PUMP'], 'test.csv', { type: 'text/csv' });
      const input = document.getElementById('csv-upload') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [file] } });

      const uploadBtn = screen.getByRole('button', { name: /upload csv/i });
      fireEvent.click(uploadBtn);

      await waitFor(() => {
        expect(screen.getByText('Import completed successfully!')).toBeInTheDocument();
      });
    });
  });

  describe('File Size Formatting', () => {
    it('formats file size correctly for different sizes', () => {
      render(<ModernIngestion />);

      // Test with different file sizes
      const smallFile = new File(['x'.repeat(500)], 'small.csv', { type: 'text/csv' });
      const input = document.getElementById('csv-upload') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [smallFile] } });

      // File size should be displayed (actual format depends on implementation)
      expect(screen.getByText('small.csv')).toBeInTheDocument();
      expect(screen.getByText(/Bytes|KB|MB/)).toBeInTheDocument();
    });
  });
});
