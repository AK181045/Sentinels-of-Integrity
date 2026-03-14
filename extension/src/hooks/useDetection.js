import { useState, useCallback } from 'react';
export function useDetection() {
  const [lastReport, setLastReport] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const scanCurrentPage = useCallback(async () => {
    setIsScanning(true);
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const response = await chrome.tabs.sendMessage(tab.id, { type: 'SCAN_PAGE' });
      if (response?.report) setLastReport(response.report);
    } catch (err) { console.error('Scan failed:', err); }
    finally { setIsScanning(false); }
  }, []);
  return { lastReport, isScanning, scanCurrentPage };
}
