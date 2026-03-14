// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title MultiSigValidator
 * @notice 3-of-5 multi-signature validation for ledger updates.
 * (TechStack.txt §3: "Multi-Sig Wallets: Requiring 3-of-5 approvals")
 */
contract MultiSigValidator {
    uint256 public constant REQUIRED_APPROVALS = 3;
    uint256 public constant MAX_VALIDATORS = 5;

    address[] public validators;
    mapping(address => bool) public isValidator;

    struct Proposal {
        bytes32 contentHash;
        address proposer;
        uint256 approvalCount;
        bool executed;
        mapping(address => bool) approvals;
    }

    uint256 public proposalCount;
    mapping(uint256 => Proposal) public proposals;

    event ProposalCreated(uint256 indexed id, bytes32 contentHash, address proposer);
    event ProposalApproved(uint256 indexed id, address validator);
    event ProposalExecuted(uint256 indexed id, bytes32 contentHash);

    modifier onlyValidator() {
        require(isValidator[msg.sender], "Not a validator");
        _;
    }

    constructor(address[] memory _validators) {
        require(_validators.length == MAX_VALIDATORS, "Need exactly 5 validators");
        for (uint i = 0; i < _validators.length; i++) {
            validators.push(_validators[i]);
            isValidator[_validators[i]] = true;
        }
    }

    function createProposal(bytes32 _contentHash) external onlyValidator returns (uint256) {
        uint256 id = proposalCount++;
        Proposal storage p = proposals[id];
        p.contentHash = _contentHash;
        p.proposer = msg.sender;
        p.approvalCount = 1;
        p.approvals[msg.sender] = true;
        emit ProposalCreated(id, _contentHash, msg.sender);
        return id;
    }

    function approveProposal(uint256 _id) external onlyValidator {
        Proposal storage p = proposals[_id];
        require(!p.executed, "Already executed");
        require(!p.approvals[msg.sender], "Already approved");
        p.approvals[msg.sender] = true;
        p.approvalCount++;
        emit ProposalApproved(_id, msg.sender);

        if (p.approvalCount >= REQUIRED_APPROVALS) {
            p.executed = true;
            emit ProposalExecuted(_id, p.contentHash);
        }
    }

    function getProposalStatus(uint256 _id) external view returns (
        bytes32 contentHash, address proposer, uint256 approvals, bool executed
    ) {
        Proposal storage p = proposals[_id];
        return (p.contentHash, p.proposer, p.approvalCount, p.executed);
    }
}
