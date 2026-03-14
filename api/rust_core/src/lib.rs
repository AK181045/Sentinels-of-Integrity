// =============================================================================
// SENTINELS OF INTEGRITY — Rust Core Library
// Entry point exposing all cryptographic modules to Python via PyO3 FFI.
// =============================================================================
//
// SECURITY DIRECTIVE (Design.txt §6, TechStack.txt §2):
// "Critical hashing modules must be written in Rust, not Python."
// This crate provides memory-safe implementations of:
//   - SHA-256 hashing (for media integrity)
//   - AES-256-GCM encryption (for data at rest)
//   - RS256 / X.509 signing (for JWT and content signing)
// =============================================================================

mod hasher;
mod encryption;
mod signer;

use pyo3::prelude::*;

/// Sentinels Core — Python module exposed via PyO3.
/// 
/// Usage from Python:
/// ```python
/// import sentinels_core
/// 
/// # Hash media bytes
/// digest = sentinels_core.sha256_hash(b"media bytes...")
/// 
/// # Encrypt data at rest
/// key = sentinels_core.generate_aes_key()
/// ciphertext, nonce = sentinels_core.aes_encrypt(key, b"secret data")
/// plaintext = sentinels_core.aes_decrypt(key, ciphertext, nonce)
/// 
/// # Sign data with RSA
/// private_key, public_key = sentinels_core.generate_rsa_keypair()
/// signature = sentinels_core.rsa_sign(private_key, b"data to sign")
/// is_valid = sentinels_core.rsa_verify(public_key, b"data to sign", signature)
/// ```
#[pymodule]
fn sentinels_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // --- Hashing ---
    m.add_function(wrap_pyfunction!(hasher::sha256_hash, m)?)?;
    m.add_function(wrap_pyfunction!(hasher::sha256_hash_file, m)?)?;
    m.add_function(wrap_pyfunction!(hasher::sha256_hash_hex, m)?)?;
    m.add_function(wrap_pyfunction!(hasher::verify_hash, m)?)?;

    // --- Encryption ---
    m.add_function(wrap_pyfunction!(encryption::generate_aes_key, m)?)?;
    m.add_function(wrap_pyfunction!(encryption::aes_encrypt, m)?)?;
    m.add_function(wrap_pyfunction!(encryption::aes_decrypt, m)?)?;
    m.add_function(wrap_pyfunction!(encryption::aes_encrypt_file, m)?)?;
    m.add_function(wrap_pyfunction!(encryption::aes_decrypt_file, m)?)?;

    // --- Signing ---
    m.add_function(wrap_pyfunction!(signer::generate_rsa_keypair, m)?)?;
    m.add_function(wrap_pyfunction!(signer::rsa_sign, m)?)?;
    m.add_function(wrap_pyfunction!(signer::rsa_verify, m)?)?;
    m.add_function(wrap_pyfunction!(signer::generate_jwt, m)?)?;
    m.add_function(wrap_pyfunction!(signer::verify_jwt, m)?)?;

    // Module metadata
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add("__description__", env!("CARGO_PKG_DESCRIPTION"))?;

    Ok(())
}
