// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ContentRegistry
 * @notice Creator registration and edit history tracking.
 * @dev Implements C2PA-compatible metadata storage.
 */
contract ContentRegistry {
    struct ContentRecord {
        bytes32 contentHash;
        address creator;
        string metadataURI;     // IPFS/Arweave URI for C2PA metadata
        uint256 registeredAt;
        uint256 editCount;
        bool exists;
    }

    struct EditEntry {
        address editor;
        bytes32 editHash;
        string description;
        uint256 timestamp;
    }

    mapping(bytes32 => ContentRecord) public contents;
    mapping(bytes32 => EditEntry[]) public editHistory;
    mapping(address => bytes32[]) public creatorContents;

    event ContentRegistered(bytes32 indexed contentHash, address indexed creator, string metadataURI);
    event ContentEdited(bytes32 indexed originalHash, bytes32 indexed editHash, address editor);

    function registerContent(bytes32 _hash, string calldata _metadataURI) external {
        require(!contents[_hash].exists, "Already registered");
        contents[_hash] = ContentRecord({
            contentHash: _hash,
            creator: msg.sender,
            metadataURI: _metadataURI,
            registeredAt: block.timestamp,
            editCount: 0,
            exists: true
        });
        creatorContents[msg.sender].push(_hash);
        emit ContentRegistered(_hash, msg.sender, _metadataURI);
    }

    function recordEdit(bytes32 _originalHash, bytes32 _editHash, string calldata _description) external {
        require(contents[_originalHash].exists, "Original not found");
        editHistory[_originalHash].push(EditEntry({
            editor: msg.sender,
            editHash: _editHash,
            description: _description,
            timestamp: block.timestamp
        }));
        contents[_originalHash].editCount++;
        emit ContentEdited(_originalHash, _editHash, msg.sender);
    }

    function getEditHistory(bytes32 _hash) external view returns (EditEntry[] memory) {
        return editHistory[_hash];
    }

    function getContent(bytes32 _hash) external view returns (ContentRecord memory) {
        return contents[_hash];
    }
}
