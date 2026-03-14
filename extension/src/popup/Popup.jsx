import React, { useState, useEffect } from 'react';
import TrustScore from '../components/TrustScore';
import AnalysisPanel from '../components/AnalysisPanel';
import SettingsPanel from '../components/SettingsPanel';
import ReportHistory from '../components/ReportHistory';
import { useDetection } from '../hooks/useDetection';
import { useSettings } from '../hooks/useSettings';
import './Popup.css';

const TABS = ['scan', 'history', 'settings'];

export default function Popup() {
  const [activeTab, setActiveTab] = useState('scan');
  const { lastReport, isScanning, scanCurrentPage } = useDetection();
  const { settings, updateSetting } = useSettings();

  return (
    <div className="sentinel-popup">
      <header className="popup-header">
        <div className="logo">🛡️</div>
        <h1>Sentinels of Integrity</h1>
      </header>

      <nav className="popup-nav">
        {TABS.map(tab => (
          <button
            key={tab}
            className={`nav-btn ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab === 'scan' ? '🔍 Scan' : tab === 'history' ? '📋 History' : '⚙️ Settings'}
          </button>
        ))}
      </nav>

      <main className="popup-content">
        {activeTab === 'scan' && (
          <div className="scan-tab">
            <button className="scan-btn" onClick={scanCurrentPage} disabled={isScanning}>
              {isScanning ? 'Analyzing...' : 'Scan Current Page'}
            </button>
            {lastReport && (
              <>
                <TrustScore score={lastReport.sentinels_score} verdict={lastReport.verdict} />
                <AnalysisPanel report={lastReport} />
              </>
            )}
          </div>
        )}
        {activeTab === 'history' && <ReportHistory />}
        {activeTab === 'settings' && <SettingsPanel settings={settings} onUpdate={updateSetting} />}
      </main>

      <footer className="popup-footer">
        <span>v0.1.0 · Powered by AI + Blockchain</span>
      </footer>
    </div>
  );
}
