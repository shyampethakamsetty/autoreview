import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import ReviewsTable from './components/ReviewsTable';
import ReviewDetail from './pages/ReviewDetail';
import Analytics from './pages/Analytics';
const Ingest = React.lazy(() => import('./pages/Ingest'));
import { ErrorBoundary } from './components/ErrorBoundary';

function Navigation() {
  const location = useLocation();
  
  const isActive = (path: string) => {
    return location.pathname === path;
  };

  const linkStyle = (path: string) => ({
    padding: '10px 20px',
    textDecoration: 'none',
    color: isActive(path) ? 'white' : '#007bff',
    backgroundColor: isActive(path) ? '#007bff' : 'transparent',
    borderRadius: '4px',
    fontWeight: isActive(path) ? 'bold' : 'normal',
    transition: 'all 0.2s'
  });

  return (
    <nav style={{ 
      backgroundColor: '#f8f9fa', 
      padding: '15px 20px',
      marginBottom: '20px',
      borderBottom: '2px solid #dee2e6'
    }}>
      <div style={{ 
        maxWidth: '1200px', 
        margin: '0 auto',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '15px'
      }}>
        <h1 style={{ margin: 0, fontSize: '24px' }}>Reviews Copilot</h1>
        <div style={{ display: 'flex', gap: '10px' }}>
          <Link to="/" style={linkStyle('/')}>
            📥 Inbox
          </Link>
          <Link to="/analytics" style={linkStyle('/analytics')}>
            📊 Analytics
          </Link>
          <Link to="/ingest" style={linkStyle('/ingest')}>
            ➕ Ingest
          </Link>
        </div>
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
          <Navigation />
          <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
            <ErrorBoundary>
              <Routes>
                <Route path="/" element={
                  <ErrorBoundary>
                    <ReviewsTable />
                  </ErrorBoundary>
                } />
                <Route path="/review/:id" element={
                  <ErrorBoundary>
                    <ReviewDetail />
                  </ErrorBoundary>
                } />
                <Route path="/analytics" element={
                  <ErrorBoundary>
                    <Analytics />
                  </ErrorBoundary>
                } />
                <Route path="/ingest" element={
                  <ErrorBoundary>
                    <React.Suspense fallback={<div>Loading...</div>}>
                      <Ingest />
                    </React.Suspense>
                  </ErrorBoundary>
                } />
              </Routes>
            </ErrorBoundary>
          </div>
        </div>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
