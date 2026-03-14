// =============================================================================
// SENTINELS OF INTEGRITY — RSA Signer Module
// Memory-safe cryptographic signing for JWT tokens and content provenance.
// =============================================================================
//
// SECURITY DIRECTIVES (TechStack.txt §2):
// - "JWT with RS256: Asymmetric signing to prevent token forgery."
// - "C2PA: Signed with X.509 Certificates."
// =============================================================================

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use rsa::{
    RsaPrivateKey, RsaPublicKey,
    pkcs8::{EncodePrivateKey, EncodePublicKey, DecodePrivateKey, DecodePublicKey, LineEnding},
    pkcs1v15::{SigningKey, VerifyingKey},
};
use sha2::Sha256;
use signature::{Signer, Verifier};
use base64::{Engine as _, engine::general_purpose::URL_SAFE_NO_PAD};
use rand::rngs::OsRng;

/// Generate a new RSA-2048 key pair for RS256 signing.
///
/// # Returns
/// * Tuple of (private_key_pem, public_key_pem) as strings
///
/// # Example (Python)
/// ```python
/// private_key, public_key = sentinels_core.generate_rsa_keypair()
/// ```
#[pyfunction]
pub fn generate_rsa_keypair() -> PyResult<(String, String)> {
    let mut rng = OsRng;
    let bits = 2048;

    let private_key = RsaPrivateKey::new(&mut rng, bits)
        .map_err(|e| PyValueError::new_err(format!("RSA key generation failed: {}", e)))?;

    let public_key = RsaPublicKey::from(&private_key);

    let private_pem = private_key
        .to_pkcs8_pem(LineEnding::LF)
        .map_err(|e| PyValueError::new_err(format!("Failed to encode private key: {}", e)))?;

    let public_pem = public_key
        .to_public_key_pem(LineEnding::LF)
        .map_err(|e| PyValueError::new_err(format!("Failed to encode public key: {}", e)))?;

    Ok((private_pem.to_string(), public_pem))
}

/// Sign data using RSA PKCS#1 v1.5 with SHA-256 (RS256).
///
/// # Arguments
/// * `private_key_pem` - PEM-encoded RSA private key
/// * `data` - Raw bytes to sign
///
/// # Returns
/// * Base64url-encoded signature string
///
/// # Example (Python)
/// ```python
/// signature = sentinels_core.rsa_sign(private_key, b"data to sign")
/// ```
#[pyfunction]
pub fn rsa_sign(private_key_pem: &str, data: &[u8]) -> PyResult<String> {
    let private_key = RsaPrivateKey::from_pkcs8_pem(private_key_pem)
        .map_err(|e| PyValueError::new_err(format!("Invalid private key: {}", e)))?;

    let signing_key = SigningKey::<Sha256>::new(private_key);
    let signature = signing_key.sign(data);

    Ok(URL_SAFE_NO_PAD.encode(signature.to_bytes()))
}

/// Verify an RS256 signature against data using the public key.
///
/// # Arguments
/// * `public_key_pem` - PEM-encoded RSA public key
/// * `data` - Original data that was signed
/// * `signature_b64` - Base64url-encoded signature to verify
///
/// # Returns
/// * `true` if the signature is valid, `false` otherwise
///
/// # Example (Python)
/// ```python
/// is_valid = sentinels_core.rsa_verify(public_key, b"data", signature)
/// ```
#[pyfunction]
pub fn rsa_verify(public_key_pem: &str, data: &[u8], signature_b64: &str) -> PyResult<bool> {
    let public_key = RsaPublicKey::from_public_key_pem(public_key_pem)
        .map_err(|e| PyValueError::new_err(format!("Invalid public key: {}", e)))?;

    let signature_bytes = URL_SAFE_NO_PAD
        .decode(signature_b64)
        .map_err(|e| PyValueError::new_err(format!("Invalid base64 signature: {}", e)))?;

    let verifying_key = VerifyingKey::<Sha256>::new(public_key);
    
    let signature = rsa::pkcs1v15::Signature::try_from(signature_bytes.as_slice())
        .map_err(|e| PyValueError::new_err(format!("Invalid signature format: {}", e)))?;

    match verifying_key.verify(data, &signature) {
        Ok(()) => Ok(true),
        Err(_) => Ok(false),
    }
}

/// Generate a minimal JWT token signed with RS256.
///
/// Creates a JWT with the given claims JSON and signs it using the private key.
/// Format: base64url(header).base64url(payload).base64url(signature)
///
/// # Arguments
/// * `private_key_pem` - PEM-encoded RSA private key
/// * `claims_json` - JSON string of JWT claims (payload)
///
/// # Returns
/// * Complete JWT token string
///
/// # Example (Python)
/// ```python
/// import json
/// claims = json.dumps({"sub": "user123", "exp": 1700000000})
/// token = sentinels_core.generate_jwt(private_key, claims)
/// ```
#[pyfunction]
pub fn generate_jwt(private_key_pem: &str, claims_json: &str) -> PyResult<String> {
    // JWT Header (RS256)
    let header = r#"{"alg":"RS256","typ":"JWT"}"#;
    let header_b64 = URL_SAFE_NO_PAD.encode(header.as_bytes());
    let payload_b64 = URL_SAFE_NO_PAD.encode(claims_json.as_bytes());

    // Signing input: header.payload
    let signing_input = format!("{}.{}", header_b64, payload_b64);
    let signature = rsa_sign(private_key_pem, signing_input.as_bytes())?;

    Ok(format!("{}.{}", signing_input, signature))
}

/// Verify a JWT token's signature using the public key.
///
/// Validates the RS256 signature but does NOT validate claims (expiry, issuer, etc.)
/// — that logic belongs in the Python middleware layer.
///
/// # Arguments
/// * `public_key_pem` - PEM-encoded RSA public key
/// * `token` - Complete JWT token string
///
/// # Returns
/// * `true` if the signature is valid, `false` otherwise
///
/// # Example (Python)
/// ```python
/// is_valid = sentinels_core.verify_jwt(public_key, token)
/// ```
#[pyfunction]
pub fn verify_jwt(public_key_pem: &str, token: &str) -> PyResult<bool> {
    let parts: Vec<&str> = token.splitn(3, '.').collect();
    if parts.len() != 3 {
        return Err(PyValueError::new_err("Invalid JWT format: expected 3 dot-separated parts"));
    }

    let signing_input = format!("{}.{}", parts[0], parts[1]);
    rsa_verify(public_key_pem, signing_input.as_bytes(), parts[2])
}

// =============================================================================
// Unit Tests
// =============================================================================
#[cfg(test)]
mod tests {
    use super::*;

    fn test_keypair() -> (String, String) {
        generate_rsa_keypair().unwrap()
    }

    #[test]
    fn test_keypair_generation() {
        let (private_key, public_key) = test_keypair();
        assert!(private_key.contains("BEGIN PRIVATE KEY"));
        assert!(public_key.contains("BEGIN PUBLIC KEY"));
    }

    #[test]
    fn test_sign_verify_roundtrip() {
        let (private_key, public_key) = test_keypair();
        let data = b"Sentinels of Integrity — signing test";

        let signature = rsa_sign(&private_key, data).unwrap();
        let is_valid = rsa_verify(&public_key, data, &signature).unwrap();

        assert!(is_valid);
    }

    #[test]
    fn test_wrong_data_fails_verification() {
        let (private_key, public_key) = test_keypair();
        let signature = rsa_sign(&private_key, b"original data").unwrap();
        let is_valid = rsa_verify(&public_key, b"tampered data", &signature).unwrap();

        assert!(!is_valid);
    }

    #[test]
    fn test_wrong_key_fails_verification() {
        let (private_key1, _) = test_keypair();
        let (_, public_key2) = test_keypair();
        let data = b"test";

        let signature = rsa_sign(&private_key1, data).unwrap();
        let is_valid = rsa_verify(&public_key2, data, &signature).unwrap();

        assert!(!is_valid);
    }

    #[test]
    fn test_jwt_roundtrip() {
        let (private_key, public_key) = test_keypair();
        let claims = r#"{"sub":"user123","role":"admin"}"#;

        let token = generate_jwt(&private_key, claims).unwrap();
        
        // Verify token has 3 parts
        assert_eq!(token.split('.').count(), 3);

        let is_valid = verify_jwt(&public_key, &token).unwrap();
        assert!(is_valid);
    }

    #[test]
    fn test_jwt_tampered_payload() {
        let (private_key, public_key) = test_keypair();
        let claims = r#"{"sub":"user123"}"#;

        let token = generate_jwt(&private_key, claims).unwrap();
        
        // Tamper with the payload
        let parts: Vec<&str> = token.splitn(3, '.').collect();
        let tampered_payload = URL_SAFE_NO_PAD.encode(r#"{"sub":"admin"}"#.as_bytes());
        let tampered_token = format!("{}.{}.{}", parts[0], tampered_payload, parts[2]);

        let is_valid = verify_jwt(&public_key, &tampered_token).unwrap();
        assert!(!is_valid);
    }

    #[test]
    fn test_jwt_invalid_format() {
        let (_, public_key) = test_keypair();
        let result = verify_jwt(&public_key, "not.a.valid.jwt.with.too.many.parts");
        // splitn(3, '.') should still work, but signature verification should fail
        assert!(result.is_ok());
    }
}
