import React, { useState, useEffect } from 'react';
import { getStorage } from '../utils/storage';
export default function ReportHistory() {
  const [reports, setReports] = useState([]);
  useEffect(() => { getStorage('history').then(h => setReports(h || [])); }, []);
  const colors = { authentic: '#2ea043', suspicious: '#d29922', synthetic: '#f85149' };
  return (
    <div>
      {reports.length === 0 && <p style={{ color: '#8b949e', textAlign: 'center', fontSize: '13px' }}>No scans yet. Analyze a video to see results here.</p>}
      {reports.map((r, i) => (
        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #21262d', fontSize: '12px' }}>
          <div>
            <div style={{ color: '#e6edf3', fontWeight: 500 }}>{r.platform}</div>
            <div style={{ color: '#8b949e' }}>{r.media_hash?.slice(0, 12)}...</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ color: colors[r.verdict], fontWeight: 600 }}>{Math.round(r.sentinels_score)}</div>
            <div style={{ color: '#8b949e', fontSize: '11px' }}>{r.verdict}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
