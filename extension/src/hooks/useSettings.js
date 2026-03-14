import { useState, useEffect } from 'react';
import { getStorage, setStorage } from '../utils/storage';

const DEFAULTS = { auto_scan: true, show_overlay: true, confidence_threshold: 0.7, notification_enabled: true };

export function useSettings() {
  const [settings, setSettings] = useState(DEFAULTS);
  useEffect(() => { getStorage('settings').then(s => setSettings({ ...DEFAULTS, ...s })); }, []);
  const updateSetting = async (key, value) => {
    const updated = { ...settings, [key]: value };
    setSettings(updated);
    await setStorage('settings', updated);
  };
  return { settings, updateSetting };
}
