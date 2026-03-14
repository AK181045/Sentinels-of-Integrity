"""
=============================================================================
SENTINELS OF INTEGRITY — Unit Test: Blockchain Service
Tests blockchain hash verification and content registration.
=============================================================================
"""

import pytest
from api.app.services.blockchain_service import BlockchainService
from api.app.models.schemas import BlockchainVerificationResponse


class TestBlockchainService:
    """Tests for BlockchainService."""

    @pytest.fixture
    def service(self):
        return BlockchainService()

    @pytest.fixture
    def valid_hash(self):
        return "abcdef1234567890" * 4  # 64 hex chars

    @pytest.fixture
    def valid_address(self):
        return "0x" + "A" * 40

    # =========================================================================
    # Test: Hash Verification
    # =========================================================================

    @pytest.mark.asyncio
    async def test_verify_hash_returns_response(self, service, valid_hash):
        """verify_hash should return a BlockchainVerificationResponse."""
        result = await service.verify_hash(valid_hash)
        assert isinstance(result, BlockchainVerificationResponse)

    @pytest.mark.asyncio
    async def test_verify_hash_contains_required_fields(self, service, valid_hash):
        """Response should have content_hash, is_registered, and lookup_latency_ms."""
        result = await service.verify_hash(valid_hash)
        assert result.content_hash == valid_hash
        assert isinstance(result.is_registered, bool)
        assert result.lookup_latency_ms >= 0

    @pytest.mark.asyncio
    async def test_verify_hash_unregistered_content(self, service, valid_hash):
        """Unregistered content should return is_registered=False."""
        result = await service.verify_hash(valid_hash)
        assert result.is_registered is False
        assert result.author is None

    @pytest.mark.asyncio
    async def test_verify_hash_with_history(self, service, valid_hash):
        """When include_history=True, edit_history should be a list."""
        result = await service.verify_hash(valid_hash, include_history=True)
        assert isinstance(result.edit_history, list)

    @pytest.mark.asyncio
    async def test_verify_hash_latency_under_target(self, service, valid_hash):
        """Hash lookup latency should be < 500ms (Design.txt §5 target)."""
        result = await service.verify_hash(valid_hash)
        assert result.lookup_latency_ms < 500, (
            f"Latency {result.lookup_latency_ms}ms exceeds 500ms target"
        )

    # =========================================================================
    # Test: Content Registration
    # =========================================================================

    @pytest.mark.asyncio
    async def test_register_content_returns_tx_hash(self, service, valid_hash, valid_address):
        """register_content should return a transaction hash string."""
        tx_hash = await service.register_content(valid_hash, valid_address)
        assert isinstance(tx_hash, str)
        assert tx_hash.startswith("0x")

    @pytest.mark.asyncio
    async def test_register_content_with_metadata(self, service, valid_hash, valid_address):
        """Registration with metadata should succeed."""
        metadata = {"title": "Test Video", "standard": "C2PA"}
        tx_hash = await service.register_content(valid_hash, valid_address, metadata=metadata)
        assert isinstance(tx_hash, str)

    # =========================================================================
    # Test: ZK Proof Verification
    # =========================================================================

    @pytest.mark.asyncio
    async def test_verify_zk_proof_default_false(self, service, valid_hash):
        """ZK proof verification should return False when not implemented."""
        result = await service.verify_zk_proof(valid_hash, b"fake_proof")
        assert result is False

    # =========================================================================
    # Test: Merkle Proof
    # =========================================================================

    @pytest.mark.asyncio
    async def test_get_merkle_proof_returns_none(self, service, valid_hash):
        """Merkle proof should return None for unregistered content."""
        result = await service.get_merkle_proof(valid_hash)
        assert result is None
