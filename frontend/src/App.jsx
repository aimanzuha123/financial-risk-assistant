import React, { useState } from 'react';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import UploadPage from './pages/Upload';
import EDAPage from './pages/EDA';
import PredictionsPage from './pages/Predictions';
import ReportsPage from './pages/Reports';
import CollectionsPage from './pages/Collections';
import AIChatPage from './pages/AIChat';
import SettingsPage from './pages/Settings';

export default function App() {
  const [activePage, setActivePage] = useState('dashboard');

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':
        return <Dashboard setActivePage={setActivePage} />;
      case 'upload':
        return <UploadPage />;
      case 'eda':
        return <EDAPage />;
      case 'predictions':
        return <PredictionsPage />;
      case 'report':
        return <ReportsPage />;
      case 'collections':
        return <CollectionsPage />;
      case 'chat':
        return <AIChatPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <Dashboard setActivePage={setActivePage} />;
    }
  };

  return (
    <Layout activePage={activePage} setActivePage={setActivePage}>
      {renderPage()}
    </Layout>
  );
}
