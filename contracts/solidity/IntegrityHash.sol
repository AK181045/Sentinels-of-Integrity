// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title IntegrityHash
 * @notice Mints SHA-256 integrity hashes on Polygon zkEVM.
 * @dev Stores content hashes as permanent provenance records.
 *      Data: SHA-256 Hash + timestamp (Design.txt §4)
 */
contract IntegrityHash {
    struct HashRecord {
        bytes32 contentHash;
        address creator;
        uint256 timestamp;
        bool exists;
    }

    mapping(bytes32 => HashRecord) public records;
    mapping(address => bytes32[]) public creatorHashes;

    event HashRegistered(bytes32 indexed contentHash, address indexed creator, uint256 timestamp);
    event HashVerified(bytes32 indexed contentHash, bool exists);

    modifier onlyNewHash(bytes32 _hash) {
        require(!records[_hash].exists, "Hash already registered");
        _;
    }

    function registerHash(bytes32 _contentHash) external onlyNewHash(_contentHash) {
        records[_contentHash] = HashRecord({
            contentHash: _contentHash,
            creator: msg.sender,
            timestamp: block.timestamp,
            exists: true
        });
        creatorHashes[msg.sender].push(_contentHash);
        emit HashRegistered(_contentHash, msg.sender, block.timestamp);
    }

    function verifyHash(bytes32 _contentHash) external view returns (bool exists, address creator, uint256 timestamp) {
        HashRecord memory record = records[_contentHash];
        return (record.exists, record.creator, record.timestamp);
    }

    function getCreatorHashes(address _creator) external view returns (bytes32[] memory) {
        return creatorHashes[_creator];
    }

    function isRegistered(bytes32 _contentHash) external view returns (bool) {
        return records[_contentHash].exists;
    }
}
