import React from 'react';
export default function SettingsPanel({ settings, onUpdate }) {
  return (
    <div style={{ display: 'grid', gap: '12px' }}>
      <Toggle label="Auto-scan videos" checked={settings?.auto_scan} onChange={v => onUpdate('auto_scan', v)} />
      <Toggle label="Show overlay on videos" checked={settings?.show_overlay} onChange={v => onUpdate('show_overlay', v)} />
      <Toggle label="Notifications" checked={settings?.notification_enabled} onChange={v => onUpdate('notification_enabled', v)} />
      <div style={{ fontSize: '12px', color: '#8b949e', marginTop: '8px' }}>
        Confidence Threshold: {((settings?.confidence_threshold || 0.7) * 100).toFixed(0)}%
      </div>
    </div>
  );
}
function Toggle({ label, checked, onChange }) {
  return (
    <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid #21262d', cursor: 'pointer', fontSize: '13px' }}>
      <span>{label}</span>
      <input type="checkbox" checked={checked || false} onChange={e => onChange(e.target.checked)} />
    </label>
  );
}
