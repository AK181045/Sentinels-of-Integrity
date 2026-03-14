// =============================================================================
// SENTINELS OF INTEGRITY — Rust Core Integration Tests
// End-to-end tests for all cryptographic primitives.
// =============================================================================

#[cfg(test)]
mod integration_tests {
    // Note: These tests import from the library crate.
    // Run with: cargo test --test core_tests

    use std::fs;
    use tempfile::NamedTempFile;
    use std::io::Write;

    // =========================================================================
    // Hasher Integration Tests
    // =========================================================================

    #[test]
    fn test_hash_large_data() {
        // Simulate hashing a 10MB "video file"
        let data = vec![0xABu8; 10 * 1024 * 1024]; // 10 MB
        let hash = sentinels_core::sha256_hash(&data);
        assert_eq!(hash.len(), 64); // SHA-256 hex = 64 chars

        // Verify determinism
        let hash2 = sentinels_core::sha256_hash(&data);
        assert_eq!(hash, hash2);
    }

    #[test]
    fn test_hash_file_matches_hash_bytes() {
        let content = b"Test file content for Sentinels";

        // Write to temp file
        let mut tmp = NamedTempFile::new().unwrap();
        tmp.write_all(content).unwrap();
        let path = tmp.path().to_str().unwrap();

        // Hash via file and via bytes should match
        let file_hash = sentinels_core::sha256_hash_file(path).unwrap();
        let bytes_hash = sentinels_core::sha256_hash(content);

        assert_eq!(file_hash, bytes_hash);
    }

    // =========================================================================
    // Encryption Integration Tests
    // =========================================================================

    #[test]
    fn test_encrypt_decrypt_various_sizes() {
        let key = sentinels_core::generate_aes_key();

        // Test with various data sizes
        let sizes: Vec<usize> = vec![0, 1, 15, 16, 17, 256, 1024, 65536];

        for size in sizes {
            let data = vec![0x42u8; size];
            let (ciphertext, nonce) = sentinels_core::aes_encrypt(&key, &data).unwrap();
            let decrypted = sentinels_core::aes_decrypt(&key, &ciphertext, &nonce).unwrap();
            assert_eq!(decrypted, data, "Failed for size {}", size);
        }
    }

    #[test]
    fn test_file_encrypt_decrypt_roundtrip() {
        let key = sentinels_core::generate_aes_key();
        let original_content = b"Sensitive media hash data that must be encrypted at rest";

        // Create temp file
        let mut tmp = NamedTempFile::new().unwrap();
        tmp.write_all(original_content).unwrap();
        let path = tmp.path().to_str().unwrap().to_string();

        // Encrypt the file
        let _nonce = sentinels_core::aes_encrypt_file(&key, &path).unwrap();

        // Verify file content changed
        let encrypted_data = fs::read(&path).unwrap();
        assert_ne!(encrypted_data, original_content.to_vec());

        // Decrypt the file
        let decrypted = sentinels_core::aes_decrypt_file(&key, &path).unwrap();
        assert_eq!(decrypted, original_content.to_vec());
    }

    // =========================================================================
    // Signer Integration Tests
    // =========================================================================

    #[test]
    fn test_full_jwt_workflow() {
        // 1. Generate keypair
        let (private_key, public_key) = sentinels_core::generate_rsa_keypair().unwrap();

        // 2. Create claims
        let claims = r#"{"sub":"sentinel-api","iss":"sentinels-of-integrity","iat":1700000000,"exp":1700003600}"#;

        // 3. Generate JWT
        let token = sentinels_core::generate_jwt(&private_key, claims).unwrap();

        // 4. Verify JWT
        assert!(sentinels_core::verify_jwt(&public_key, &token).unwrap());

        // 5. Verify with wrong key fails
        let (_, wrong_public_key) = sentinels_core::generate_rsa_keypair().unwrap();
        assert!(!sentinels_core::verify_jwt(&wrong_public_key, &token).unwrap());
    }

    #[test]
    fn test_content_provenance_signing() {
        // Simulate C2PA-style content provenance signing
        let (private_key, public_key) = sentinels_core::generate_rsa_keypair().unwrap();

        // 1. Hash the media content
        let media_data = b"simulated video frame data";
        let media_hash = sentinels_core::sha256_hash(media_data);

        // 2. Sign the hash (this would be the C2PA assertion signature)
        let signature = sentinels_core::rsa_sign(&private_key, media_hash.as_bytes()).unwrap();

        // 3. Verify the signature
        assert!(sentinels_core::rsa_verify(
            &public_key,
            media_hash.as_bytes(),
            &signature
        ).unwrap());

        // 4. Verify tampered hash is rejected
        let tampered_hash = sentinels_core::sha256_hash(b"different content");
        assert!(!sentinels_core::rsa_verify(
            &public_key,
            tampered_hash.as_bytes(),
            &signature
        ).unwrap());
    }

    // =========================================================================
    // Cross-Module Integration Tests
    // =========================================================================

    #[test]
    fn test_hash_encrypt_sign_pipeline() {
        // Full pipeline: Hash → Encrypt → Sign (as would happen in production)

        let aes_key = sentinels_core::generate_aes_key();
        let (rsa_private, rsa_public) = sentinels_core::generate_rsa_keypair().unwrap();

        // 1. Hash the media
        let media = b"video frame data for deepfake analysis";
        let hash = sentinels_core::sha256_hash(media);

        // 2. Encrypt the hash for storage
        let (encrypted_hash, nonce) = sentinels_core::aes_encrypt(&aes_key, hash.as_bytes()).unwrap();

        // 3. Sign the encrypted hash for tamper-proof transit
        let signature = sentinels_core::rsa_sign(&rsa_private, &encrypted_hash).unwrap();

        // ---- Verification side ----

        // 4. Verify the signature
        assert!(sentinels_core::rsa_verify(&rsa_public, &encrypted_hash, &signature).unwrap());

        // 5. Decrypt the hash
        let decrypted_hash = sentinels_core::aes_decrypt(&aes_key, &encrypted_hash, &nonce).unwrap();
        assert_eq!(String::from_utf8(decrypted_hash).unwrap(), hash);

        // 6. Verify the hash matches the original media
        assert!(sentinels_core::verify_hash(media, &hash));
    }
}
