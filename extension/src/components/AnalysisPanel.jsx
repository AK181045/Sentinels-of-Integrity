import React from 'react';
export default function AnalysisPanel({ report }) {
  if (!report) return null;
  const { ml_result, blockchain_result } = report;
  return (
    <div style={{ marginTop: '16px', background: '#161b22', borderRadius: '8px', padding: '12px', fontSize: '12px' }}>
      <h3 style={{ margin: '0 0 8px', fontSize: '13px', color: '#58a6ff' }}>Analysis Breakdown</h3>
      <div style={{ display: 'grid', gap: '6px' }}>
        <Row label="ML Confidence" value={`${(ml_result?.confidence * 100).toFixed(1)}%`} />
        <Row label="Synthetic" value={ml_result?.is_synthetic ? 'Yes' : 'No'} />
        <Row label="Artifacts" value={ml_result?.artifacts?.join(', ') || 'None'} />
        <Row label="Blockchain Registered" value={blockchain_result?.is_registered ? 'Yes ✅' : 'No'} />
        <Row label="ZK Verified" value={blockchain_result?.zk_verified ? 'Yes' : 'No'} />
      </div>
    </div>
  );
}
function Row({ label, value }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid #21262d' }}>
      <span style={{ color: '#8b949e' }}>{label}</span>
      <span style={{ color: '#e6edf3' }}>{value}</span>
    </div>
  );
}
