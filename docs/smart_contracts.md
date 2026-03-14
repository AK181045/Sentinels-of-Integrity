# Sentinels of Integrity — Smart Contract Documentation

## Overview

The blockchain component runs on **Polygon zkEVM** and consists of five contracts:

| Contract | Purpose | Key Functions |
|----------|---------|---------------|
| `IntegrityHash` | SHA-256 hash minting | `registerHash`, `verifyHash` |
| `ContentRegistry` | Creator registration + edit history | `registerContent`, `recordEdit` |
| `MultiSigValidator` | 3-of-5 governance | `createProposal`, `approveProposal` |
| `ZKVerifier` | ZK proof verification | `verifyProof`, `isVerified` |
| `MerkleProof` | Media chunk integrity | `storeMerkleRoot`, `verifyProof` |

## Contract Details

### IntegrityHash

Stores SHA-256 content hashes as permanent provenance records.

```solidity
function registerHash(bytes32 _contentHash) external;
function verifyHash(bytes32 _contentHash) external view returns (bool, address, uint256);
function isRegistered(bytes32 _contentHash) external view returns (bool);
```

**Events:**
- `HashRegistered(bytes32 contentHash, address creator, uint256 timestamp)`
- `HashVerified(bytes32 contentHash, bool exists)`

### ContentRegistry

Manages creator registration with C2PA-compatible metadata.

```solidity
function registerContent(bytes32 _hash, string _metadataURI) external;
function recordEdit(bytes32 _originalHash, bytes32 _editHash, string _description) external;
function getEditHistory(bytes32 _hash) external view returns (EditEntry[] memory);
```

### MultiSigValidator

Requires 3 of 5 validator approvals for critical operations.

```solidity
function createProposal(bytes32 _contentHash) external returns (uint256 id);
function approveProposal(uint256 _id) external;
function getProposalStatus(uint256 _id) external view returns (...);
```

### ZKVerifier

Verifies Circom/Groth16 zero-knowledge proofs for anonymous verification.

```solidity
function verifyProof(bytes32 _contentHash, bytes _proof, uint256[] _publicInputs) external returns (bool);
function isVerified(bytes32 _contentHash) external view returns (bool);
```

### MerkleProof

Ensures media chunks haven't been swapped using Merkle tree verification.

```solidity
function storeMerkleRoot(bytes32 _contentHash, bytes32 _merkleRoot) external;
function verifyProof(bytes32[] _proof, bytes32 _root, bytes32 _leaf) external pure returns (bool);
```

## Deployment

```bash
cd contracts
npm install
npx hardhat compile
npx hardhat test
npx hardhat run scripts/deploy.js --network polygon_zkevm_testnet
```

## Gas Estimates (Polygon zkEVM)

| Operation | Estimated Gas | ~Cost (MATIC) |
|-----------|--------------|---------------|
| registerHash | ~65,000 | ~$0.01 |
| registerContent | ~120,000 | ~$0.02 |
| recordEdit | ~85,000 | ~$0.01 |
| createProposal | ~95,000 | ~$0.01 |
| verifyProof (Merkle) | ~45,000 | ~$0.01 |
