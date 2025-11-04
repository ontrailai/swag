import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { Navbar } from './components/Navbar';
import { SplashScreen } from './components/SplashScreen';
import { Dashboard } from './pages/Dashboard';
import { Upload } from './pages/Upload';
import { Settings } from './pages/Settings';
import { History } from './pages/History';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  const [showSplash, setShowSplash] = useState(true);

  if (showSplash) {
    return <SplashScreen onComplete={() => setShowSplash(false)} />;
  }

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="flex min-h-screen bg-swag-dark">
          <Navbar />
          <main className="flex-1 ml-64 p-8 max-w-[1440px]">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/upload" element={<Upload />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/history" element={<History />} />
            </Routes>
          </main>
        </div>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1C1C1C',
              color: '#F8F8F8',
              border: '2px solid #32FF6A',
              borderRadius: '12px',
              padding: '16px',
              fontSize: '14px',
              fontWeight: '600',
            },
            success: {
              iconTheme: {
                primary: '#32FF6A',
                secondary: '#0F0F0F',
              },
            },
            error: {
              iconTheme: {
                primary: '#FF3B30',
                secondary: '#0F0F0F',
              },
            },
          }}
        />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
