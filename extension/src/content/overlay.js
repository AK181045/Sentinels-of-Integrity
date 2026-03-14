/**
 * SENTINELS OF INTEGRITY — Trust HUD Overlay
 * Non-intrusive visual overlay on video elements showing trust score.
 */

export function createOverlay(videoElement) {
  const container = document.createElement('div');
  container.className = 'sentinel-overlay';
  container.innerHTML = `
    <div class="sentinel-badge" title="Sentinels of Integrity">
      <span class="sentinel-icon">🛡️</span>
      <span class="sentinel-score">--</span>
    </div>
  `;

  // Position relative to video
  const parent = videoElement.parentElement;
  if (parent) {
    parent.style.position = parent.style.position || 'relative';
    parent.appendChild(container);
  }

  return container;
}

export function updateOverlay(overlay, report) {
  if (!overlay || !report) return;

  const scoreEl = overlay.querySelector('.sentinel-score');
  const badgeEl = overlay.querySelector('.sentinel-badge');

  const score = Math.round(report.sentinels_score);
  scoreEl.textContent = score;

  // Color based on verdict
  const colors = {
    authentic: '#2ea043',
    suspicious: '#d29922',
    synthetic: '#f85149',
  };
  badgeEl.style.borderColor = colors[report.verdict] || '#8b949e';
  badgeEl.title = `Trust Score: ${score}/100 — ${report.verdict.toUpperCase()}`;
}
