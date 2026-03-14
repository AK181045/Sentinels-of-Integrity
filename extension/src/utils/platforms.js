/**
 * SENTINELS OF INTEGRITY — Platform DOM Adapters
 * Detects platform and finds video elements for YouTube, X, and TikTok.
 */
export function detectPlatform(url) {
  if (url.includes('youtube.com')) return 'youtube';
  if (url.includes('twitter.com') || url.includes('x.com')) return 'twitter';
  if (url.includes('tiktok.com')) return 'tiktok';
  return null;
}

export function getVideoElements(platform) {
  const selectors = {
    youtube: 'video.html5-main-video, ytd-player video',
    twitter: 'video[src], div[data-testid="videoPlayer"] video',
    tiktok: 'video.tiktok-web-player, div[class*="DivVideoContainer"] video',
  };
  return [...document.querySelectorAll(selectors[platform] || 'video')];
}
