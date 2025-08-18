import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box, Container } from '@mui/material';

import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';

// Pages
import LoginPage from './pages/Auth/LoginPage';
import DashboardPage from './pages/Dashboard/DashboardPage';
import StocksPage from './pages/Stocks/StocksPage';
import WatchlistPage from './pages/Watchlist/WatchlistPage';
import ReportsPage from './pages/Reports/ReportsPage';
import ReportDetailPage from './pages/Reports/ReportDetailPage';
import AnalysisPage from './pages/Analysis/AnalysisPage';
import SettingsPage from './pages/Settings/SettingsPage';
import PricingPage from './pages/Pricing/PricingPage';
import NotFoundPage from './pages/NotFound/NotFoundPage';

function App() {
  return (
    <AuthProvider>
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
        <Routes>
          {/* 公开路由 */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/pricing" element={<PricingPage />} />
          
          {/* 受保护的路由 */}
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <Layout>
                  <Container maxWidth="xl" sx={{ py: 3 }}>
                    <Routes>
                      <Route path="/" element={<DashboardPage />} />
                      <Route path="/dashboard" element={<DashboardPage />} />
                      <Route path="/stocks" element={<StocksPage />} />
                      <Route path="/watchlist" element={<WatchlistPage />} />
                      <Route path="/analysis" element={<AnalysisPage />} />
                      <Route path="/reports" element={<ReportsPage />} />
                      <Route path="/reports/:reportId" element={<ReportDetailPage />} />
                      <Route path="/settings" element={<SettingsPage />} />
                      <Route path="*" element={<NotFoundPage />} />
                    </Routes>
                  </Container>
                </Layout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </Box>
    </AuthProvider>
  );
}

export default App;
