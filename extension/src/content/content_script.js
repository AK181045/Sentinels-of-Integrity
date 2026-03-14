/**
 * SENTINELS OF INTEGRITY — Content Script
 * Injected into YouTube, X, and TikTok pages.
 * Detects video elements and attaches Trust HUD overlay.
 */

import { detectPlatform, getVideoElements } from '../utils/platforms';
import { createOverlay, updateOverlay } from './overlay';
import { computeLocalHash } from './local_hasher';

const SCAN_INTERVAL = 5000; // Re-scan for new videos every 5s

async function init() {
  const platform = detectPlatform(window.location.href);
  if (!platform) return;

  console.log(`[Sentinels] Initialized on ${platform}`);
  scanForVideos(platform);

  // Observe DOM changes for dynamically loaded videos
  const observer = new MutationObserver(() => scanForVideos(platform));
  observer.observe(document.body, { childList: true, subtree: true });
}

async function scanForVideos(platform) {
  const videos = getVideoElements(platform);

  for (const video of videos) {
    if (video.dataset.sentinelScanned) continue;
    video.dataset.sentinelScanned = 'true';

    // Create overlay
    const overlay = createOverlay(video);

    // Request analysis from background service worker
    try {
      const hash = await computeLocalHash(video.src || window.location.href);
      const response = await chrome.runtime.sendMessage({
        type: 'ANALYZE_MEDIA',
        payload: { mediaUrl: window.location.href, mediaHash: hash, platform },
      });

      if (response && response.report) {
        updateOverlay(overlay, response.report);
      }
    } catch (err) {
      console.error('[Sentinels] Analysis failed:', err);
    }
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
