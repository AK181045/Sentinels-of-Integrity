/**
 * SENTINELS OF INTEGRITY — Client-Side Local Hasher
 * Computes SHA-256 hashes locally — no raw video ever leaves the browser.
 * (TechStack.txt §4: "Local-first hashing. No raw video is ever uploaded, only the hash.")
 */

export async function computeLocalHash(input) {
  let data;
  if (typeof input === 'string') {
    data = new TextEncoder().encode(input);
  } else if (input instanceof ArrayBuffer) {
    data = new Uint8Array(input);
  } else if (input instanceof Uint8Array) {
    data = input;
  } else {
    data = new TextEncoder().encode(String(input));
  }

  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}
