import { Routes, Route } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import { RecordPage } from '@/pages/RecordPage';
import { LibraryPage } from '@/pages/LibraryPage';
import { TranscriptDetailPage } from '@/pages/TranscriptDetailPage';
import { SettingsPage } from '@/pages/SettingsPage';

function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<RecordPage />} />
        <Route path="/library" element={<LibraryPage />} />
        <Route path="/library/:recordingId" element={<TranscriptDetailPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </AppLayout>
  );
}

export default App;
