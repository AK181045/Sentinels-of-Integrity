"""
=============================================================================
SENTINELS OF INTEGRITY — Unit Test: Rust Hasher (FFI Boundary)
Tests the Python-to-Rust FFI boundary for SHA-256 hashing.
=============================================================================

NOTE: These tests require the Rust core to be built via maturin:
  cd api/rust_core && maturin develop --release

If sentinels_core is not available, tests will be skipped gracefully.
"""

import pytest
import os
import tempfile

try:
    import sentinels_core
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

skip_without_rust = pytest.mark.skipif(
    not RUST_AVAILABLE,
    reason="Rust core (sentinels_core) not built. Run: cd api/rust_core && maturin develop"
)


@skip_without_rust
class TestRustHasher:
    """Tests for Rust SHA-256 hasher via PyO3 FFI."""

    def test_sha256_empty_bytes(self):
        """SHA-256 of empty input should match known digest."""
        digest = sentinels_core.sha256_hash(b"")
        assert digest == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    def test_sha256_hello_world(self):
        """SHA-256 of 'Hello, World!' should match known digest."""
        digest = sentinels_core.sha256_hash(b"Hello, World!")
        assert digest == "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"

    def test_sha256_deterministic(self):
        """Same input should always produce same hash."""
        data = b"Sentinels of Integrity"
        hash1 = sentinels_core.sha256_hash(data)
        hash2 = sentinels_core.sha256_hash(data)
        assert hash1 == hash2

    def test_sha256_different_inputs(self):
        """Different inputs should produce different hashes."""
        hash1 = sentinels_core.sha256_hash(b"input_a")
        hash2 = sentinels_core.sha256_hash(b"input_b")
        assert hash1 != hash2

    def test_sha256_hex_length(self):
        """SHA-256 hex digest should always be 64 characters."""
        digest = sentinels_core.sha256_hash(b"any data")
        assert len(digest) == 64

    def test_sha256_hash_file(self):
        """File hashing should match direct bytes hashing."""
        content = b"Test file content for Sentinels integrity check"
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            file_hash = sentinels_core.sha256_hash_file(tmp_path)
            bytes_hash = sentinels_core.sha256_hash(content)
            assert file_hash == bytes_hash
        finally:
            os.unlink(tmp_path)

    def test_sha256_hash_file_nonexistent(self):
        """Hashing a nonexistent file should raise IOError."""
        with pytest.raises(IOError):
            sentinels_core.sha256_hash_file("/nonexistent/file.bin")

    def test_verify_hash_correct(self):
        """verify_hash should return True for matching hash."""
        data = b"verify me"
        correct_hash = sentinels_core.sha256_hash(data)
        assert sentinels_core.verify_hash(data, correct_hash) is True

    def test_verify_hash_incorrect(self):
        """verify_hash should return False for mismatched hash."""
        data = b"original"
        wrong_hash = "0" * 64
        assert sentinels_core.verify_hash(data, wrong_hash) is False

    def test_sha256_hash_hex_raw_bytes(self):
        """sha256_hash_hex should return 32 raw bytes."""
        raw = sentinels_core.sha256_hash_hex(b"test data")
        assert len(raw) == 32
        assert isinstance(raw, (bytes, list))


@skip_without_rust
class TestRustEncryption:
    """Tests for Rust AES-256-GCM encryption via PyO3 FFI."""

    def test_generate_key_length(self):
        """Generated key should be 32 bytes (256 bits)."""
        key = sentinels_core.generate_aes_key()
        assert len(key) == 32

    def test_generate_key_unique(self):
        """Two generated keys should be different."""
        key1 = sentinels_core.generate_aes_key()
        key2 = sentinels_core.generate_aes_key()
        assert key1 != key2

    def test_encrypt_decrypt_roundtrip(self):
        """Encrypt then decrypt should recover original plaintext."""
        key = sentinels_core.generate_aes_key()
        plaintext = b"Sensitive media hash data"
        ciphertext, nonce = sentinels_core.aes_encrypt(key, plaintext)
        decrypted = sentinels_core.aes_decrypt(key, ciphertext, nonce)
        assert decrypted == plaintext

    def test_ciphertext_differs_from_plaintext(self):
        """Ciphertext should not equal plaintext."""
        key = sentinels_core.generate_aes_key()
        plaintext = b"secret data"
        ciphertext, _ = sentinels_core.aes_encrypt(key, plaintext)
        assert ciphertext != plaintext

    def test_wrong_key_fails(self):
        """Decryption with wrong key should fail."""
        key1 = sentinels_core.generate_aes_key()
        key2 = sentinels_core.generate_aes_key()
        ciphertext, nonce = sentinels_core.aes_encrypt(key1, b"data")
        with pytest.raises(Exception):
            sentinels_core.aes_decrypt(key2, ciphertext, nonce)


@skip_without_rust
class TestRustSigner:
    """Tests for Rust RSA signer via PyO3 FFI."""

    def test_keypair_generation(self):
        """Should generate valid PEM-encoded key pair."""
        private_key, public_key = sentinels_core.generate_rsa_keypair()
        assert "BEGIN PRIVATE KEY" in private_key
        assert "BEGIN PUBLIC KEY" in public_key

    def test_sign_verify_roundtrip(self):
        """Signature should verify with correct public key."""
        private_key, public_key = sentinels_core.generate_rsa_keypair()
        data = b"Content to sign"
        signature = sentinels_core.rsa_sign(private_key, data)
        assert sentinels_core.rsa_verify(public_key, data, signature) is True

    def test_jwt_roundtrip(self):
        """JWT should verify with correct key pair."""
        private_key, public_key = sentinels_core.generate_rsa_keypair()
        claims = '{"sub":"test","role":"admin"}'
        token = sentinels_core.generate_jwt(private_key, claims)
        assert sentinels_core.verify_jwt(public_key, token) is True
