import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { Dashboard } from './pages/Dashboard';
import { Notes } from './pages/Notes';
import { Drawing } from './pages/Drawing';
import { Tasks } from './pages/Tasks';
import { Roadmap } from './pages/Roadmap';
import { Graph } from './pages/Graph';
import { Settings } from './pages/Settings';

function App() {
  return (
    <BrowserRouter>
      <AppLayout>
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/notes" element={<Notes />} />
            <Route path="/drawing" element={<Drawing />} />
            <Route path="/tasks" element={<Tasks />} />
            <Route path="/roadmap" element={<Roadmap />} />
            <Route path="/graph" element={<Graph />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </div>
      </AppLayout>
    </BrowserRouter>
  );
}

export default App;
