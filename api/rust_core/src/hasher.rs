// =============================================================================
// SENTINELS OF INTEGRITY — SHA-256 Hasher Module
// Memory-safe hashing for media integrity verification.
// =============================================================================
//
// SECURITY DIRECTIVES:
// - DATA MINIMIZATION: "Never store raw video files. Store only HASHES (SHA-256)."
// - MEMORY SAFETY: "Critical hashing modules must be written in Rust, not Python."
// =============================================================================

use pyo3::prelude::*;
use pyo3::exceptions::PyIOError;
use sha2::{Sha256, Digest};
use std::fs::File;
use std::io::{BufReader, Read};

/// Compute the SHA-256 hash of raw bytes and return the hex digest.
///
/// # Arguments
/// * `data` - Raw bytes to hash (e.g., media content)
///
/// # Returns
/// * Hex-encoded SHA-256 digest string (64 characters)
///
/// # Example (Python)
/// ```python
/// digest = sentinels_core.sha256_hash(b"Hello, World!")
/// # => "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
/// ```
#[pyfunction]
pub fn sha256_hash(data: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data);
    let result = hasher.finalize();
    hex::encode(result)
}

/// Compute the SHA-256 hash of raw bytes and return raw bytes (32 bytes).
///
/// # Arguments
/// * `data` - Raw bytes to hash
///
/// # Returns
/// * Raw 32-byte SHA-256 digest
#[pyfunction]
pub fn sha256_hash_hex(data: &[u8]) -> Vec<u8> {
    let mut hasher = Sha256::new();
    hasher.update(data);
    hasher.finalize().to_vec()
}

/// Compute the SHA-256 hash of a file by streaming it in chunks.
/// 
/// This avoids loading the entire file into memory, which is critical
/// for large video files.
///
/// # Arguments
/// * `file_path` - Absolute path to the file to hash
///
/// # Returns
/// * Hex-encoded SHA-256 digest string
///
/// # Errors
/// * Returns `PyIOError` if the file cannot be opened or read
///
/// # Example (Python)
/// ```python
/// digest = sentinels_core.sha256_hash_file("/path/to/video.mp4")
/// ```
#[pyfunction]
pub fn sha256_hash_file(file_path: &str) -> PyResult<String> {
    let file = File::open(file_path)
        .map_err(|e| PyIOError::new_err(format!("Failed to open file '{}': {}", file_path, e)))?;

    let mut reader = BufReader::with_capacity(1024 * 1024, file); // 1 MB buffer
    let mut hasher = Sha256::new();
    let mut buffer = vec![0u8; 1024 * 1024]; // 1 MB read chunks

    loop {
        let bytes_read = reader.read(&mut buffer)
            .map_err(|e| PyIOError::new_err(format!("Failed to read file '{}': {}", file_path, e)))?;

        if bytes_read == 0 {
            break;
        }
        hasher.update(&buffer[..bytes_read]);
    }

    let result = hasher.finalize();
    Ok(hex::encode(result))
}

/// Verify that a given hash matches the SHA-256 digest of the provided data.
///
/// # Arguments
/// * `data` - Raw bytes to verify
/// * `expected_hash` - Expected hex-encoded SHA-256 digest
///
/// # Returns
/// * `true` if the hashes match, `false` otherwise
///
/// # Example (Python)
/// ```python
/// is_valid = sentinels_core.verify_hash(b"data", "expected_hex_hash")
/// ```
#[pyfunction]
pub fn verify_hash(data: &[u8], expected_hash: &str) -> bool {
    let computed = sha256_hash(data);
    // Constant-time comparison to prevent timing attacks
    constant_time_eq(computed.as_bytes(), expected_hash.as_bytes())
}

/// Constant-time byte comparison to prevent timing side-channel attacks.
fn constant_time_eq(a: &[u8], b: &[u8]) -> bool {
    if a.len() != b.len() {
        return false;
    }
    let mut result: u8 = 0;
    for (x, y) in a.iter().zip(b.iter()) {
        result |= x ^ y;
    }
    result == 0
}

// =============================================================================
// Unit Tests
// =============================================================================
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sha256_empty() {
        let digest = sha256_hash(b"");
        assert_eq!(digest, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
    }

    #[test]
    fn test_sha256_hello() {
        let digest = sha256_hash(b"Hello, World!");
        assert_eq!(digest, "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f");
    }

    #[test]
    fn test_sha256_deterministic() {
        let data = b"Sentinels of Integrity";
        let hash1 = sha256_hash(data);
        let hash2 = sha256_hash(data);
        assert_eq!(hash1, hash2);
    }

    #[test]
    fn test_verify_hash_valid() {
        let data = b"test data";
        let hash = sha256_hash(data);
        assert!(verify_hash(data, &hash));
    }

    #[test]
    fn test_verify_hash_invalid() {
        let data = b"test data";
        assert!(!verify_hash(data, "0000000000000000000000000000000000000000000000000000000000000000"));
    }

    #[test]
    fn test_sha256_hex_length() {
        let raw = sha256_hash_hex(b"test");
        assert_eq!(raw.len(), 32); // SHA-256 = 32 bytes
    }
}
