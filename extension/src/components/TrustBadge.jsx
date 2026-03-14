import React from 'react';
export default function TrustBadge({ score, verdict }) {
  const colors = { authentic: '#2ea043', suspicious: '#d29922', synthetic: '#f85149' };
  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '4px 10px', background: 'rgba(13,17,23,0.8)', border: `2px solid ${colors[verdict] || '#8b949e'}`, borderRadius: '16px', fontSize: '13px', fontWeight: 600, color: '#e6edf3' }}>
      <span>🛡️</span>
      <span>{Math.round(score)}</span>
    </div>
  );
}
