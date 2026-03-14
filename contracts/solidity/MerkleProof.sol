// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title MerkleProof
 * @notice Merkle tree verification for media chunk integrity.
 * (TechStack.txt §3: "Merkle Tree structures to ensure media chunks aren't swapped")
 */
contract MerkleProof {
    mapping(bytes32 => bytes32) public merkleRoots;

    event MerkleRootStored(bytes32 indexed contentHash, bytes32 merkleRoot);

    function storeMerkleRoot(bytes32 _contentHash, bytes32 _merkleRoot) external {
        merkleRoots[_contentHash] = _merkleRoot;
        emit MerkleRootStored(_contentHash, _merkleRoot);
    }

    function verifyProof(
        bytes32[] calldata _proof,
        bytes32 _root,
        bytes32 _leaf
    ) external pure returns (bool) {
        bytes32 computedHash = _leaf;
        for (uint256 i = 0; i < _proof.length; i++) {
            if (computedHash <= _proof[i]) {
                computedHash = keccak256(abi.encodePacked(computedHash, _proof[i]));
            } else {
                computedHash = keccak256(abi.encodePacked(_proof[i], computedHash));
            }
        }
        return computedHash == _root;
    }

    function getMerkleRoot(bytes32 _contentHash) external view returns (bytes32) {
        return merkleRoots[_contentHash];
    }
}
