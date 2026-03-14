# Sentinels of Integrity — Extension Developer Guide

## Architecture

```
extension/
├── public/
│   ├── manifest.json      ← Manifest V3 configuration
│   └── popup.html         ← Popup entry point
├── src/
│   ├── popup/
│   │   ├── index.jsx      ← React mount point
│   │   ├── Popup.jsx      ← Main popup component
│   │   └── Popup.css      ← Popup styles
│   ├── content/
│   │   ├── content_script.js  ← Injected into YouTube/X/TikTok
│   │   ├── overlay.js     ← Trust HUD overlay
│   │   ├── overlay.css    ← Overlay styles
│   │   └── local_hasher.js ← SHA-256 via Web Crypto API
│   ├── background/
│   │   └── service_worker.js  ← API communication + caching
│   ├── components/
│   │   ├── TrustScore.jsx     ← SVG circular score display
│   │   ├── TrustBadge.jsx     ← Compact inline badge
│   │   ├── AnalysisPanel.jsx  ← ML/Blockchain result breakdown
│   │   ├── SettingsPanel.jsx  ← User preferences
│   │   └── ReportHistory.jsx  ← Past scan history
│   ├── hooks/
│   │   ├── useDetection.js    ← Detection state management
│   │   └── useSettings.js     ← Settings persistence
│   ├── utils/
│   │   ├── api.js         ← API client
│   │   ├── platforms.js   ← Platform-specific DOM selectors
│   │   └── storage.js     ← Chrome storage wrappers
│   └── styles/
│       └── global.css     ← Global styles
├── package.json
└── vite.config.js         ← Multi-entry build config
```

## Security Hardening

### Content Security Policy (CSP)
```json
"content_security_policy": {
  "extension_pages": "script-src 'self'; object-src 'none'"
}
```

### Permissions (Minimal)
- `activeTab` — Only access the current tab
- `storage` — For caching results and settings
- `alarms` — For periodic tasks

### Privacy
- **Local-first hashing:** SHA-256 is computed in the browser using `crypto.subtle.digest`. No raw video data ever leaves the extension.
- **Minimal data sent:** Only `{ hash, url, platform }` is sent to the API.

## Development

```bash
cd extension
npm install
npm run dev     # Development with hot reload
npm run build   # Production build → dist/
```

### Loading in Chrome
1. Go to `chrome://extensions`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `dist/` folder

## Platform Selectors

| Platform | Video Element Selectors |
|----------|------------------------|
| YouTube | `video.html5-main-video`, `ytd-player video` |
| Twitter/X | `video[src]`, `div[data-testid="videoPlayer"] video` |
| TikTok | `video.tiktok-web-player`, `div[class*="DivVideoContainer"] video` |

## Adding a New Platform

1. Add URL pattern to `manifest.json` → `host_permissions` and `content_scripts.matches`
2. Add selector to `src/utils/platforms.js` → `getVideoElements()`
3. Add platform to API schema: `api/app/models/schemas.py` → `Platform` enum
4. Add to shared constants: `shared/types/constants.py`
