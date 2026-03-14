/**
 * SENTINELS OF INTEGRITY — Service Worker (Background)
 * Handles API communication and caching.
 */

import { apiRequest } from '../utils/api';
import { getStorage, setStorage } from '../utils/storage';

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'ANALYZE_MEDIA') {
    handleAnalysis(message.payload).then(sendResponse);
    return true; // Keep channel open for async response
  }
});

async function handleAnalysis({ mediaUrl, mediaHash, platform }) {
  // Check cache first
  const cached = await getStorage(`report:${mediaHash}`);
  if (cached) return { report: cached, cached: true };

  try {
    const report = await apiRequest('/api/v1/detect', 'POST', {
      media_hash: mediaHash,
      media_url: mediaUrl,
      platform: platform,
      media_type: 'video',
    });

    // Cache the result
    await setStorage(`report:${mediaHash}`, report);
    return { report, cached: false };
  } catch (error) {
    console.error('[Sentinels] API error:', error);
    return { error: error.message };
  }
}
