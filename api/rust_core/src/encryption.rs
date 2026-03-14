// =============================================================================
// SENTINELS OF INTEGRITY — AES-256-GCM Encryption Module
// Memory-safe encryption for data at rest.
// =============================================================================
//
// SECURITY DIRECTIVE (Design.txt §6):
// "All data at rest must use AES-256-GCM."
// =============================================================================

use pyo3::prelude::*;
use pyo3::exceptions::{PyValueError, PyIOError};
use aes_gcm::{
    aead::{Aead, KeyInit, OsRng},
    Aes256Gcm, Key, Nonce,
};
use rand::RngCore;
use std::fs;

/// Generate a new random 256-bit AES key.
///
/// # Returns
/// * 32 random bytes suitable for AES-256-GCM encryption
///
/// # Example (Python)
/// ```python
/// key = sentinels_core.generate_aes_key()
/// assert len(key) == 32
/// ```
#[pyfunction]
pub fn generate_aes_key() -> Vec<u8> {
    let mut key_bytes = vec![0u8; 32];
    OsRng.fill_bytes(&mut key_bytes);
    key_bytes
}

/// Encrypt data using AES-256-GCM.
///
/// # Arguments
/// * `key` - 32-byte AES key
/// * `plaintext` - Data to encrypt
///
/// # Returns
/// * Tuple of (ciphertext_bytes, nonce_bytes)
/// * The nonce (12 bytes) must be stored alongside the ciphertext for decryption
///
/// # Errors
/// * `PyValueError` if the key is not exactly 32 bytes
/// * `PyValueError` if encryption fails
///
/// # Example (Python)
/// ```python
/// key = sentinels_core.generate_aes_key()
/// ciphertext, nonce = sentinels_core.aes_encrypt(key, b"secret data")
/// ```
#[pyfunction]
pub fn aes_encrypt(key: &[u8], plaintext: &[u8]) -> PyResult<(Vec<u8>, Vec<u8>)> {
    if key.len() != 32 {
        return Err(PyValueError::new_err(
            format!("AES-256 key must be exactly 32 bytes, got {}", key.len())
        ));
    }

    let aes_key = Key::<Aes256Gcm>::from_slice(key);
    let cipher = Aes256Gcm::new(aes_key);

    // Generate a random 96-bit nonce (12 bytes)
    let mut nonce_bytes = [0u8; 12];
    OsRng.fill_bytes(&mut nonce_bytes);
    let nonce = Nonce::from_slice(&nonce_bytes);

    let ciphertext = cipher
        .encrypt(nonce, plaintext)
        .map_err(|e| PyValueError::new_err(format!("Encryption failed: {}", e)))?;

    Ok((ciphertext, nonce_bytes.to_vec()))
}

/// Decrypt data using AES-256-GCM.
///
/// # Arguments
/// * `key` - 32-byte AES key (same key used for encryption)
/// * `ciphertext` - Encrypted data
/// * `nonce` - 12-byte nonce used during encryption
///
/// # Returns
/// * Decrypted plaintext bytes
///
/// # Errors
/// * `PyValueError` if key is not 32 bytes or nonce is not 12 bytes
/// * `PyValueError` if decryption fails (wrong key, tampered data, etc.)
///
/// # Example (Python)
/// ```python
/// plaintext = sentinels_core.aes_decrypt(key, ciphertext, nonce)
/// ```
#[pyfunction]
pub fn aes_decrypt(key: &[u8], ciphertext: &[u8], nonce: &[u8]) -> PyResult<Vec<u8>> {
    if key.len() != 32 {
        return Err(PyValueError::new_err(
            format!("AES-256 key must be exactly 32 bytes, got {}", key.len())
        ));
    }
    if nonce.len() != 12 {
        return Err(PyValueError::new_err(
            format!("Nonce must be exactly 12 bytes, got {}", nonce.len())
        ));
    }

    let aes_key = Key::<Aes256Gcm>::from_slice(key);
    let cipher = Aes256Gcm::new(aes_key);
    let nonce = Nonce::from_slice(nonce);

    let plaintext = cipher
        .decrypt(nonce, ciphertext)
        .map_err(|_| PyValueError::new_err(
            "Decryption failed: invalid key, corrupted ciphertext, or tampered data"
        ))?;

    Ok(plaintext)
}

/// Encrypt a file in place using AES-256-GCM.
/// 
/// Reads the file, encrypts its contents, and writes the ciphertext back.
/// The nonce is prepended to the file (first 12 bytes).
///
/// # Arguments
/// * `key` - 32-byte AES key
/// * `file_path` - Path to the file to encrypt
///
/// # Returns
/// * Nonce bytes (12 bytes) — also prepended to the encrypted file
///
/// # Errors
/// * `PyIOError` if the file cannot be read or written
/// * `PyValueError` if encryption fails
#[pyfunction]
pub fn aes_encrypt_file(key: &[u8], file_path: &str) -> PyResult<Vec<u8>> {
    let plaintext = fs::read(file_path)
        .map_err(|e| PyIOError::new_err(format!("Failed to read file '{}': {}", file_path, e)))?;

    let (ciphertext, nonce) = aes_encrypt(key, &plaintext)?;

    // Prepend nonce to ciphertext for self-contained encrypted file
    let mut output = nonce.clone();
    output.extend_from_slice(&ciphertext);

    fs::write(file_path, &output)
        .map_err(|e| PyIOError::new_err(format!("Failed to write file '{}': {}", file_path, e)))?;

    Ok(nonce)
}

/// Decrypt a file that was encrypted with `aes_encrypt_file`.
///
/// Expects the nonce to be prepended (first 12 bytes of the file).
///
/// # Arguments
/// * `key` - 32-byte AES key
/// * `file_path` - Path to the encrypted file
///
/// # Returns
/// * Decrypted plaintext bytes
///
/// # Errors
/// * `PyIOError` if the file cannot be read
/// * `PyValueError` if the file is too short or decryption fails
#[pyfunction]
pub fn aes_decrypt_file(key: &[u8], file_path: &str) -> PyResult<Vec<u8>> {
    let data = fs::read(file_path)
        .map_err(|e| PyIOError::new_err(format!("Failed to read file '{}': {}", file_path, e)))?;

    if data.len() < 12 {
        return Err(PyValueError::new_err(
            "Encrypted file is too short — must contain at least 12-byte nonce"
        ));
    }

    let (nonce, ciphertext) = data.split_at(12);
    aes_decrypt(key, ciphertext, nonce)
}

// =============================================================================
// Unit Tests
// =============================================================================
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_generate_key_length() {
        let key = generate_aes_key();
        assert_eq!(key.len(), 32);
    }

    #[test]
    fn test_generate_key_randomness() {
        let key1 = generate_aes_key();
        let key2 = generate_aes_key();
        assert_ne!(key1, key2); // Two random keys should never be equal
    }

    #[test]
    fn test_encrypt_decrypt_roundtrip() {
        let key = generate_aes_key();
        let plaintext = b"Sentinels of Integrity — AES test data";

        let (ciphertext, nonce) = aes_encrypt(&key, plaintext).unwrap();
        let decrypted = aes_decrypt(&key, &ciphertext, &nonce).unwrap();

        assert_eq!(decrypted, plaintext);
    }

    #[test]
    fn test_ciphertext_differs_from_plaintext() {
        let key = generate_aes_key();
        let plaintext = b"This should be encrypted";

        let (ciphertext, _) = aes_encrypt(&key, plaintext).unwrap();
        assert_ne!(ciphertext, plaintext.to_vec());
    }

    #[test]
    fn test_wrong_key_fails() {
        let key1 = generate_aes_key();
        let key2 = generate_aes_key();
        let plaintext = b"secret";

        let (ciphertext, nonce) = aes_encrypt(&key1, plaintext).unwrap();
        let result = aes_decrypt(&key2, &ciphertext, &nonce);

        assert!(result.is_err());
    }

    #[test]
    fn test_tampered_ciphertext_fails() {
        let key = generate_aes_key();
        let plaintext = b"integrity check";

        let (mut ciphertext, nonce) = aes_encrypt(&key, plaintext).unwrap();
        // Tamper with the ciphertext
        if let Some(byte) = ciphertext.get_mut(0) {
            *byte ^= 0xFF;
        }

        let result = aes_decrypt(&key, &ciphertext, &nonce);
        assert!(result.is_err());
    }

    #[test]
    fn test_invalid_key_size() {
        let short_key = vec![0u8; 16]; // AES-128, not AES-256
        let result = aes_encrypt(&short_key, b"data");
        assert!(result.is_err());
    }

    #[test]
    fn test_encrypt_empty_data() {
        let key = generate_aes_key();
        let (ciphertext, nonce) = aes_encrypt(&key, b"").unwrap();
        let decrypted = aes_decrypt(&key, &ciphertext, &nonce).unwrap();
        assert_eq!(decrypted, b"");
    }
}
