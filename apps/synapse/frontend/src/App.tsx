import React, { useEffect, lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { EngineeringExplorer } from './components/EngineeringExplorer';
import { CableSchedule } from './pages/CableSchedule';
import { TagManager } from './components/TagManager';
import { useAppStore } from './store/useAppStore';
import { useAuthStore } from './store/useAuthStore';
import { useProjectStore } from './store/useProjectStore';
import { useLogStore } from './store/useLogStore';
import { LoginScreen } from './components/auth/LoginScreen';
import { DevConsoleV3 } from './components/DevConsoleV3';
import { Toaster } from 'sonner';
import { setupAxiosInterceptors } from './services/axiosConfig';

// Lazy load only the heaviest components
const MetamodelEditor = lazy(() => import('./pages/MetamodelEditor'));
const RulesManagement = lazy(() => import('./pages/RulesManagement'));
const RuleExecutor = lazy(() => import('./pages/RuleExecutor'));
const Ingestion = lazy(() => import('./pages/Ingestion'));
const ModernIngestion = lazy(() => import('./pages/ModernIngestion'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const ValidationResults = lazy(() => import('./pages/ValidationResults'));

// Loading fallback component
const LoadingFallback = () => (
  <div className="flex items-center justify-center h-full bg-slate-950">
    <div className="text-center">
      <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-mining-teal mb-4"></div>
      <p className="text-slate-400">Loading...</p>
    </div>
  </div>
);

// Setup axios interceptors once when the module loads
setupAxiosInterceptors();

function AppContent() {
  const { instruments, locations, setInstruments, fetchData } = useAppStore();
  const { isAuthenticated } = useAuthStore();
  const { currentProject } = useProjectStore();
  const { clearLogs } = useLogStore();

  useEffect(() => {
    console.log("App useEffect triggered. Auth:", isAuthenticated, "Project:", currentProject?.name);
    if (isAuthenticated && currentProject) {
      clearLogs(); // Clear logs from previous project
      fetchData();
    }
  }, [fetchData, isAuthenticated, currentProject, clearLogs]);

  if (!isAuthenticated) {
    return <LoginScreen />;
  }

  return (
    <>
      <Toaster richColors position="top-right" />
      <Routes>
        <Route path="/" element={<Navigate to="/engineering" replace />} />

        <Route path="/dashboard" element={
          <Layout currentView="dashboard" setView={() => { }}>
            <Suspense fallback={<LoadingFallback />}>
              <Dashboard />
            </Suspense>
          </Layout>
        } />

        <Route path="/engineering" element={
          <Layout currentView="engineering" setView={() => { }}>
            <Suspense fallback={<LoadingFallback />}>
              <EngineeringExplorer />
            </Suspense>
          </Layout>
        } />

        <Route path="/engineering/assets/:assetId" element={
          <Layout currentView="engineering" setView={() => { }}>
            <Suspense fallback={<LoadingFallback />}>
              <EngineeringExplorer />
            </Suspense>
          </Layout>
        } />

        <Route path="/cables" element={
          <Layout currentView="cables" setView={() => { }}>
            <CableSchedule />
          </Layout>
        } />

        <Route path="/tags" element={
          <Layout currentView="tags" setView={() => { }}>
            <TagManager instruments={instruments} locations={locations} onUpdateInstruments={setInstruments} />
          </Layout>
        } />

        <Route path="/metamodel" element={
          <Layout currentView="metamodel" setView={() => { }}>
            <Suspense fallback={<LoadingFallback />}>
              <MetamodelEditor />
            </Suspense>
          </Layout>
        } />

        <Route path="/rules" element={
          <Layout currentView="rules" setView={() => { }}>
            <Suspense fallback={<LoadingFallback />}>
              <RulesManagement />
            </Suspense>
          </Layout>
        } />

        <Route path="/rule-executor" element={
          <Layout currentView="rule-executor" setView={() => { }}>
            <Suspense fallback={<LoadingFallback />}>
              <RuleExecutor />
            </Suspense>
          </Layout>
        } />

        <Route path="/ingestion" element={
          <Layout currentView="ingestion" setView={() => { }}>
            <Suspense fallback={<LoadingFallback />}>
              <Ingestion />
            </Suspense>
          </Layout>
        } />

        <Route path="/modern-ingestion" element={
          <Layout currentView="modern-ingestion" setView={() => { }}>
            <Suspense fallback={<LoadingFallback />}>
              <ModernIngestion />
            </Suspense>
          </Layout>
        } />

        <Route path="/validation-results" element={
          <Layout currentView="validation-results" setView={() => { }}>
            <Suspense fallback={<LoadingFallback />}>
              <ValidationResults />
            </Suspense>
          </Layout>
        } />
      </Routes>
      <DevConsoleV3 />
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;