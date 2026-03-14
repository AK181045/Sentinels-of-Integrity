import React from 'react';

const COLORS = { authentic: '#2ea043', suspicious: '#d29922', synthetic: '#f85149' };

export default function TrustScore({ score, verdict }) {
  const color = COLORS[verdict] || '#8b949e';
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div style={{ textAlign: 'center', padding: '20px 0' }}>
      <svg width="120" height="120" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="45" fill="none" stroke="#21262d" strokeWidth="8" />
        <circle cx="50" cy="50" r="45" fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round" transform="rotate(-90 50 50)"
          style={{ transition: 'stroke-dashoffset 1s ease' }} />
        <text x="50" y="48" textAnchor="middle" fill={color} fontSize="24" fontWeight="700">{Math.round(score)}</text>
        <text x="50" y="65" textAnchor="middle" fill="#8b949e" fontSize="10">{verdict?.toUpperCase()}</text>
      </svg>
    </div>
  );
}
