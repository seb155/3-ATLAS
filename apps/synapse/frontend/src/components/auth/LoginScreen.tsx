import React, { useState } from 'react';
import { useAuthStore } from '../../store/useAuthStore';
import { useProjectStore } from '../../store/useProjectStore';
import { Shield, Loader2 } from 'lucide-react';
import { logger } from '../../services/logger';
import apiClient from '../../services/apiClient';

export const LoginScreen = () => {
  const [email, setEmail] = useState('admin@aurumax.com');
  const [password, setPassword] = useState('admin123!');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const login = useAuthStore((state) => state.login);
  const { setCurrentClient, setCurrentProject, setAllProjects, setAllClients } = useProjectStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      console.log(' [LOGIN] Attempting login with:', { email, passwordLength: password.length });

      const response = await apiClient.post('/auth/login', formData);
      const { access_token } = response.data;

      // Set auth data
      login(access_token, { id: 'temp', email, full_name: 'User', role: 'ENGINEER' });

      // Fetch projects and set default
      try {
        const projectsRes = await apiClient.get('/projects/projects');

        // Store all projects
        setAllProjects(projectsRes.data);

        if (projectsRes.data.length > 0) {
          const firstProject = projectsRes.data[0];

          // Fetch client info
          const clientsRes = await apiClient.get('/projects/clients');

          // Store all clients
          setAllClients(clientsRes.data);

          const projectClient = clientsRes.data.find((c: { id: string;[key: string]: unknown }) => c.id === firstProject.client_id);

          if (projectClient) {
            setCurrentClient(projectClient);
          }

          setCurrentProject(firstProject);
        }
      } catch (err) {
        console.warn('Could not fetch projects:', err);
      }

      logger.success('Login successful');
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed. Please check your credentials.';
      setError(message);
      logger.error('Login failed', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-950 to-black opacity-80" />
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0icmdiYSgyNTUsMjU1LDI1NSwwLjAzKSIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyaWQpIi8+PC9zdmc+')] opacity-30" />

      {/* Login Card */}
      <div className="relative w-full max-w-md animate-in fade-in duration-500">
        {/* Logo & Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-mining-teal to-teal-600 rounded-2xl mb-6 shadow-lg shadow-mining-teal/20">
            <Shield className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-2 tracking-tight">
            AXOIQ SYNAPSE
          </h1>
          <p className="text-slate-400 text-sm">
            Engineering Data Management Platform
          </p>
          <div className="mt-2 text-xs text-slate-500">
            AuruMax Mining Corporation - v2.0 (Sprint 2)
          </div>
        </div>

        {/* Login Form */}
        <div className="bg-slate-900/95 backdrop-blur-xl border border-slate-800 rounded-2xl shadow-2xl p-8">
          <h2 className="text-2xl font-bold text-white mb-6">Sign In</h2>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-2">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-mining-teal focus:border-transparent transition-all"
                placeholder="admin@aurumax.com"
              />
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-mining-teal focus:border-transparent transition-all"
                placeholder="Enter your password"
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-900/20 border border-red-900/50 rounded-lg p-3 text-red-400 text-sm animate-in fade-in duration-200">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 px-4 bg-gradient-to-r from-mining-teal to-teal-600 hover:from-teal-600 hover:to-mining-teal text-white font-semibold rounded-lg shadow-lg shadow-mining-teal/20 hover:shadow-mining-teal/40 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-6 p-4 bg-slate-800/50 border border-slate-700 rounded-lg">
            <p className="text-xs text-slate-400 mb-2 font-medium">Demo Credentials:</p>
            <div className="text-xs text-slate-500 space-y-1 font-mono">
              <div>Email: <span className="text-mining-teal">admin@aurumax.com</span></div>
              <div>Password: <span className="text-mining-teal">admin123!</span></div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-6 text-center text-xs text-slate-600">
          Powered by AXOIQ SYNAPSE &copy; 2024
        </div>
      </div>
    </div>
  );
};
