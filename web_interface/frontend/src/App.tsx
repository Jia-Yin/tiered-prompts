import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';

import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard';
import Rules from './pages/Rules';
import RuleEditor from './pages/RuleEditor';
import Playground from './pages/Playground';
import Relationships from './pages/Relationships';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';

import { WebSocketProvider } from './contexts/WebSocketContext';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
      staleTime: 0, // Always consider data stale, will refetch more aggressively
      cacheTime: 1000 * 60 * 5, // Keep in cache for 5 minutes but consider stale immediately
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <WebSocketProvider>
        <Router>
          <div className="App">
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/rules" element={<Rules />} />
                <Route path="/rules/new" element={<RuleEditor />} />
                
                <Route path="/rules/:id/edit" element={<RuleEditor />} />
                <Route path="/playground" element={<Playground />} />
                <Route path="/relationships" element={<Relationships />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </Layout>
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
              }}
            />
          </div>
        </Router>
      </WebSocketProvider>
    </QueryClientProvider>
  );
}

export default App;