import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AssetGrid } from './AssetGrid';
import axios from 'axios';

// Mock Axios
vi.mock('axios');
const mockedAxios = axios as any;

// Mock AG Grid
vi.mock('ag-grid-react', () => ({
  AgGridReact: () => <div>AG Grid Mock</div>,
}));

vi.mock('ag-grid-community', async (importOriginal) => {
  const actual = (await importOriginal()) as any;
  return {
    ...actual,
    ModuleRegistry: {
      registerModules: vi.fn(),
    },
    ClientSideRowModelModule: {},
    themeQuartz: actual.themeQuartz || {
      withParams: vi.fn(() => ({})),
    },
  };
});

// Mock Config
vi.mock('@/config', () => ({
  API_URL: 'http://localhost:8000',
}));

// Mock Zustand Stores
vi.mock('../../store/useProjectStore', () => ({
  useProjectStore: () => ({
    currentProject: { id: 'test-project-id' },
  }),
}));

vi.mock('../../store/useAuthStore', () => ({
  useAuthStore: () => ({
    token: 'test-token',
  }),
}));

describe('AssetGrid', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders and handles export', async () => {
    const mockAssets = [
      {
        id: '1',
        tag: 'TEST-01',
        description: 'Test Asset 1',
        type: 'MOTOR',
        project_id: 'test-project-id',
      },
    ];

    render(
      <AssetGrid instruments={mockAssets as any} locations={[]} onUpdateInstruments={vi.fn()} />
    );

    // Check if "Export CSV" button is present
    const exportBtn = screen.getByText('Export');
    // console.log('Export Button HTML:', exportBtn.outerHTML);
    expect(exportBtn).toBeInTheDocument();

    // Mock Export Response
    mockedAxios.get.mockResolvedValue({
      data: new Blob(['tag,description\nTEST-01,Test Asset 1']),
    });

    // Mock URL.createObjectURL
    global.URL.createObjectURL = vi.fn();

    // Click Export
    fireEvent.click(exportBtn);

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/import_export/export',
        expect.objectContaining({
          headers: expect.objectContaining({
            'X-Project-ID': 'test-project-id',
          }),
          responseType: 'blob',
        })
      );
    });
  });
});
